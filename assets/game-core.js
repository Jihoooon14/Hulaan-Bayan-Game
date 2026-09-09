/* Browser adaptation of the existing HulaanBayan.py rules. */
(function (root) {
  'use strict';
  const DIFFICULTIES = { MADALI: 6, KATAMTAMAN: 5, MAHIRAP: 4 };
  class Game {
    constructor(words, random = Math.random) {
      this.words = words;
      this.random = random;
      this.started = false;
    }
    start(category = 'all', difficulty = 'KATAMTAMAN') {
      if (!Object.hasOwn(DIFFICULTIES, difficulty)) throw new Error('Invalid difficulty');
      if (category !== 'all' && !this.words.some(w => w.category === category)) throw new Error('Invalid category');
      this.category = category;
      this.difficulty = difficulty;
      this.maxAttempts = DIFFICULTIES[difficulty];
      this.score = this.wins = this.losses = this.bestCombo = 0;
      this.level = 1;
      this.seen = new Set();
      this.current = null;
      this.started = true;
      this.next();
    }
    next() {
      if (!this.started) return;
      const available = this.words.filter(w => this.category === 'all' || w.category === this.category);
      const poolForLevel = available.filter(w => {
        const length = w.word.replace(/[^a-z]/g, '').length;
        return this.level <= 2 ? length <= 7 : this.level <= 4 ? length >= 7 && length <= 10 : length >= 9;
      });
      const pool = poolForLevel.length ? poolForLevel : available;
      let unseen = pool.filter(w => !this.seen.has(w.word));
      if (!unseen.length) {
        pool.forEach(w => this.seen.delete(w.word));
        unseen = pool.filter(w => w.word !== this.current?.word);
        if (!unseen.length) unseen = pool;
      }
      this.current = unseen[Math.floor(this.random() * unseen.length)];
      this.seen.add(this.current.word);
      this.guessed = new Set();
      this.wrong = this.combo = 0;
      this.hintUsed = false;
      this.status = 'playing';
    }
    guess(input) {
      const letter = String(input).trim().toLowerCase();
      if (!this.started || this.status !== 'playing') return { type: 'inactive' };
      if (!/^[a-z]$/.test(letter)) return { type: 'invalid' };
      if (this.guessed.has(letter)) return { type: 'repeat', letter };
      this.guessed.add(letter);
      const correct = this.current.word.includes(letter);
      let gained = 0;
      if (correct) {
        this.combo++;
        this.bestCombo = Math.max(this.bestCombo, this.combo);
        gained = 10 + Math.min(this.combo - 1, 5) * 2;
        this.score += gained;
      } else {
        this.wrong++;
        this.combo = 0;
        this.score = Math.max(0, this.score - 5);
      }
      if ([...this.current.word].every(c => !/[a-z]/.test(c) || this.guessed.has(c))) {
        this.status = 'won';
        this.wins++;
        this.score += 50;
        this.level = 1 + Math.floor(this.wins / 2);
      } else if (this.wrong >= this.maxAttempts) {
        this.status = 'lost';
        this.losses++;
      }
      return { type: correct ? 'correct' : 'wrong', letter, gained, status: this.status };
    }
    hint() {
      if (!this.started || this.status !== 'playing' || this.hintUsed) return null;
      this.hintUsed = true;
      this.score = Math.max(0, this.score - 5);
      return this.current.hint;
    }
  }
  const api = { Game, DIFFICULTIES };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.HulaanCore = api;
})(globalThis);
