/* Original Python melody and effect sequences, with browser playback controls. */
(function (root) {
  'use strict';
  const SEQUENCES = {
    click: [[700, 45]],
    correct: [[650, 60], [850, 70], [1050, 90]],
    wrong: [[320, 100], [220, 140]],
    victory: [[523, 80], [659, 80], [784, 90], [1047, 170]],
    loss: [[500, 100], [400, 120], [320, 140], [220, 220]],
    hint: [[520, 70], [660, 70], [780, 100]],
  };
  class GameAudio {
    constructor(media, onChange, onNotice) {
      this.media = media;
      this.onChange = onChange;
      this.onNotice = onNotice;
      this.soundEnabled = this.readPreference('sound', true);
      this.musicWanted = this.readPreference('music', true);
      this.pending = false;
      this.activated = false;
      this.suspended = false;
      this.request = 0;
      this.nodes = new Set();
      media.loop = true;
      media.volume = .28;
      for (const event of ['playing', 'pause', 'ended']) media.addEventListener(event, () => this.sync());
      media.addEventListener('error', () => {
        this.pending = false;
        this.sync();
        this.onNotice('Hindi ma-play ang musika. Tap MUSIKA to try again.');
      });
      this.sync();
    }
    readPreference(name, fallback) {
      try {
        const value = root.localStorage.getItem(`hulaan-${name}`);
        return value === null ? fallback : value === 'on';
      } catch { return fallback; }
    }
    savePreference(name, value) {
      try { root.localStorage.setItem(`hulaan-${name}`, value ? 'on' : 'off'); } catch { /* Storage is optional. */ }
    }
    sync() {
      this.onChange({ sound: this.soundEnabled, music: !this.media.paused && !this.media.error, pending: this.pending });
    }
    activate() {
      this.activated = true;
      this.suspended = false;
      if (this.musicWanted) this.playMusic();
    }
    playMusic() {
      if (this.pending || !this.media.paused || this.suspended) return;
      const request = ++this.request;
      this.pending = true;
      this.onNotice('');
      this.sync();
      if (this.media.error) this.media.load();
      // Called synchronously from a tap/click, never as page-load autoplay.
      let promise;
      try { promise = this.media.play(); }
      catch (error) { promise = Promise.reject(error); }
      Promise.resolve(promise).then(() => {
        if (request !== this.request) return;
        this.pending = false;
        if (!this.musicWanted || this.suspended) this.media.pause();
        this.sync();
      }).catch(error => {
        if (request !== this.request) return;
        this.pending = false;
        this.sync();
        if (error.name !== 'AbortError') this.onNotice('Tap MUSIKA to start the background music.');
      });
    }
    toggleMusic() {
      this.activated = true;
      this.suspended = false;
      this.musicWanted = !(this.pending || !this.media.paused);
      this.savePreference('music', this.musicWanted);
      if (this.musicWanted) this.playMusic();
      else {
        ++this.request;
        this.pending = false;
        this.media.pause();
        this.onNotice('');
        this.sync();
      }
    }
    toggleSound() {
      this.soundEnabled = !this.soundEnabled;
      this.savePreference('sound', this.soundEnabled);
      if (!this.soundEnabled) this.stopEffects();
      this.sync();
      if (this.soundEnabled) this.effect('click');
    }
    effect(name) {
      if (!this.soundEnabled || this.suspended) return;
      const sequence = SEQUENCES[name];
      if (!sequence) return;
      try {
        const Context = root.AudioContext || root.webkitAudioContext;
        if (!Context) throw new Error('Web Audio unavailable');
        this.context ??= new Context();
        this.context.resume().catch(() => {});
        this.stopEffects();
        let when = this.context.currentTime;
        for (const [frequency, milliseconds] of sequence) {
          const oscillator = this.context.createOscillator();
          const gain = this.context.createGain();
          const duration = milliseconds / 1000;
          oscillator.type = 'sine';
          oscillator.frequency.value = frequency;
          gain.gain.setValueAtTime(0, when);
          gain.gain.linearRampToValueAtTime(.09, when + .008);
          gain.gain.exponentialRampToValueAtTime(.001, when + duration);
          oscillator.connect(gain).connect(this.context.destination);
          oscillator.onended = () => { this.nodes.delete(oscillator); oscillator.disconnect(); gain.disconnect(); };
          this.nodes.add(oscillator);
          oscillator.start(when);
          oscillator.stop(when + duration + .01);
          when += duration;
        }
      } catch {
        this.soundEnabled = false;
        this.sync();
        this.onNotice('Sound effects are unavailable in this browser. You can still play.');
      }
    }
    stopEffects() {
      for (const node of this.nodes) { try { node.stop(); } catch { /* Already finished. */ } }
      this.nodes.clear();
    }
    suspend() {
      this.suspended = true;
      ++this.request;
      this.pending = false;
      this.media.pause();
      this.stopEffects();
      this.context?.suspend().catch(() => {});
      this.sync();
    }
    resume() {
      this.suspended = false;
      if (this.activated && this.musicWanted) this.playMusic();
    }
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { GameAudio, SEQUENCES };
  else root.HulaanAudio = GameAudio;
})(globalThis);
