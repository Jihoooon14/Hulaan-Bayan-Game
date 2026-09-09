const test = require('node:test');
const assert = require('node:assert/strict');

// GameAudio reads and writes preferences through localStorage, which does not
// exist under Node. A minimal stand-in is enough: the class only ever calls
// getItem and setItem, and treats a throw as "storage is unavailable".
globalThis.localStorage = {
  store: new Map(),
  getItem(key) { return this.store.has(key) ? this.store.get(key) : null; },
  setItem(key, value) { this.store.set(key, value); },
};

const { GameAudio, SEQUENCES } = require('../assets/game-audio.js');

/**
 * A stand-in for the <audio> element. Real playback is not what these tests are
 * about — the interesting behaviour is when GameAudio decides to start, stop and
 * resume it, since that is what browser autoplay policy and Android
 * backgrounding constrain.
 */
function fakeMedia() {
  return {
    paused: true, loop: false, volume: 0, error: null, listeners: {},
    addEventListener(event, fn) { (this.listeners[event] ??= []).push(fn); },
    emit(event) { (this.listeners[event] || []).forEach(fn => fn()); },
    play() { this.paused = false; this.emit('playing'); return Promise.resolve(); },
    pause() { this.paused = true; this.emit('pause'); },
    load() {},
  };
}

function build() {
  globalThis.localStorage.store.clear();
  const media = fakeMedia();
  const states = [];
  const notices = [];
  const audio = new GameAudio(media, state => states.push(state), text => notices.push(text));
  return { media, states, notices, audio };
}

// GameAudio.playMusic resolves media.play() in a promise chain, so the state it
// reports settles a couple of microtasks after the call.
const settle = async () => { await Promise.resolve(); await Promise.resolve(); };

test('the theme is configured to loop, below full volume', () => {
  const { media } = build();
  assert.equal(media.loop, true);
  assert.ok(media.volume > 0 && media.volume < 1, 'background music should not play at full volume');
});

test('music does not start before a user gesture', () => {
  const { media } = build();
  assert.equal(media.paused, true, 'browsers block audio that starts on page load');
});

test('activate() starts the theme and reports it as playing', async () => {
  const { media, audio, states } = build();
  audio.activate();
  await settle();
  assert.equal(media.paused, false);
  assert.equal(states.at(-1).music, true);
});

test('MUSIKA stops and restarts the theme, remembering the choice', async () => {
  const { media, audio } = build();
  audio.activate();
  await settle();

  audio.toggleMusic();
  assert.equal(media.paused, true);
  assert.equal(globalThis.localStorage.getItem('hulaan-music'), 'off');

  audio.toggleMusic();
  await settle();
  assert.equal(media.paused, false);
  assert.equal(globalThis.localStorage.getItem('hulaan-music'), 'on');
});

test('backgrounding the app stops the theme, and returning resumes it', async () => {
  const { media, audio } = build();
  audio.activate();
  await settle();

  audio.suspend();
  assert.equal(media.paused, true, 'the theme must not play on behind the launcher');

  audio.resume();
  await settle();
  assert.equal(media.paused, false);
});

test('a suspended game does not resume music the player switched off', async () => {
  const { media, audio } = build();
  audio.activate();
  await settle();
  audio.toggleMusic();

  audio.suspend();
  audio.resume();
  await settle();
  assert.equal(media.paused, true, 'resuming must respect MUSIKA being off');
});

test('TUNOG toggles effects independently and remembers the choice', () => {
  const { audio, states } = build();
  const before = states.at(-1).sound;
  audio.toggleSound();
  assert.equal(states.at(-1).sound, !before);
  assert.equal(globalThis.localStorage.getItem('hulaan-sound'), before ? 'off' : 'on');
});

test('every melody play.js asks for exists', () => {
  // play.js calls audio.effect(...) with exactly these names.
  for (const name of ['click', 'correct', 'wrong', 'victory', 'loss', 'hint']) {
    assert.ok(SEQUENCES[name], `play.js requests the "${name}" effect, which has no melody`);
    assert.ok(SEQUENCES[name].length > 0, `the "${name}" melody is empty`);
  }
});

test('a failed track surfaces a notice rather than throwing', () => {
  const { media, notices } = build();
  media.emit('error');
  assert.ok(notices.at(-1).length > 0, 'the player should be told the music failed to load');
});
