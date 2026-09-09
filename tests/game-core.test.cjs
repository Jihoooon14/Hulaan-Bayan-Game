const test = require('node:test');
const assert = require('node:assert/strict');
const { Game, DIFFICULTIES } = require('../assets/game-core.js');
require('../assets/words.js');
const words = globalThis.HulaanWords;
const example = (word, category = 'Example') => ({ word, category, hint: 'A clue.' });

test('all Python categories and difficulty limits work', () => {
  const categories = new Set(words.map(w => w.category));
  assert.equal(categories.size, 6);
  assert.equal(words.length, 35);
  for (const category of categories) for (const [difficulty, attempts] of Object.entries(DIFFICULTIES)) {
    const game = new Game(words);
    game.start(category, difficulty);
    assert.equal(game.current.category, category);
    assert.equal(game.maxAttempts, attempts);
  }
});
test('scoring, combo cap, win bonus and completed-round guard match Python', () => {
  const game = new Game([example('abcdefgh')]);
  game.start();
  for (const letter of 'abcdefgh') game.guess(letter);
  assert.equal(game.score, 180); // 10+12+14+16+18+20+20+20, plus 50.
  assert.equal(game.status, 'won');
  assert.equal(game.wins, 1);
  assert.equal(game.bestCombo, 8);
  game.guess('z');
  assert.equal(game.score, 180);
  assert.equal(game.wrong, 0);
  game.next();
  assert.equal(game.combo, 0);
  for (const letter of 'abcdefgh') game.guess(letter);
  assert.equal(game.level, 2);
});
test('mistakes reset combo, clamp score and end each difficulty correctly', () => {
  for (const difficulty of Object.keys(DIFFICULTIES)) {
    const game = new Game([example('adobo')]);
    game.start('all', difficulty);
    game.guess('a'); game.guess('d'); game.guess('x');
    assert.equal(game.score, 17);
    assert.equal(game.combo, 0);
    for (const letter of 'zywvq'.slice(0, game.maxAttempts - 1)) game.guess(letter);
    assert.equal(game.status, 'lost');
    assert.equal(game.wrong, game.maxAttempts);
    assert.equal(game.losses, 1);
    assert.equal(game.score, Math.max(0, 22 - game.maxAttempts * 5));
  }
});
test('repeated/invalid guesses do not cost a chance or award points', () => {
  const game = new Game([example('adobo')]); game.start();
  game.guess('A');
  assert.equal(game.guess('a').type, 'repeat');
  for (const input of ['', 'aa', '1', 'é', '<']) assert.equal(game.guess(input).type, 'invalid');
  assert.equal(game.score, 10); assert.equal(game.wrong, 0);
});
test('hints can be used once, cost five and do not take the score below zero', () => {
  const game = new Game([example('adobo')]); game.start();
  game.guess('a'); assert.equal(game.hint(), 'A clue.');
  assert.equal(game.score, 5); assert.equal(game.hint(), null);
  game.next(); game.score = 0; game.hint(); assert.equal(game.score, 0);
});
test('all supplied words, spaces and hyphens can be solved', () => {
  for (const word of words) {
    const game = new Game([word]); game.start();
    for (const letter of new Set(word.word.replace(/[^a-z]/g, ''))) game.guess(letter);
    assert.equal(game.status, 'won', word.word);
  }
});
test('a campaign avoids repeats until its pool is exhausted', () => {
  const game = new Game([example('adobo'), example('piko'), example('sipa')], () => 0);
  game.start(); const first = game.current.word;
  game.next(); const second = game.current.word;
  game.next(); const third = game.current.word;
  assert.equal(new Set([first, second, third]).size, 3);
  game.next(); assert.notEqual(game.current.word, third);
});
test('level pools progress and restarting clears the campaign', () => {
  const game = new Game([example('adobo'), example('bayanihan'), example('patintero')], () => 0);
  game.start(); assert.equal(game.current.word, 'adobo');
  game.level = 3; game.next(); assert.equal(game.current.word, 'bayanihan');
  game.level = 5; game.next(); assert.equal(game.current.word, 'patintero');
  game.guess('p'); game.hint(); game.start();
  assert.equal(game.score, 0); assert.equal(game.level, 1); assert.equal(game.hintUsed, false);
});
