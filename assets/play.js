/* UI only: the game rules live in game-core.js and match the Python edition. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const game = new HulaanCore.Game(HulaanWords);
  const keys = new Map();
  let pendingAction = null;

  /* Background music and effects live in game-audio.js, which carries the
     original Python melodies and the autoplay-policy handling. */
  const audio = new HulaanAudio(
    $('music-track'),
    state => {
      $('sound').textContent = `Tunog: ${state.sound ? 'on' : 'off'}`;
      $('sound').setAttribute('aria-pressed', String(state.sound));
      const playing = state.music || state.pending;
      $('music').textContent = `Musika: ${state.pending ? '…' : state.music ? 'on' : 'off'}`;
      $('music').setAttribute('aria-pressed', String(playing));
    },
    notice => { $('audio-notice').textContent = notice; }
  );

  [...new Set(HulaanWords.map(w => w.category))].forEach(category => {
    $('category').add(new Option(category, category));
  });
  ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM'].forEach(row => {
    const container = document.createElement('div');
    container.className = 'key-row';
    for (const letter of row) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'key';
      button.textContent = letter;
      button.setAttribute('aria-label', `Guess ${letter}`);
      button.addEventListener('click', () => guess(letter));
      keys.set(letter.toLowerCase(), button);
      container.append(button);
    }
    $('keyboard').append(container);
  });

  function message(text, type = '') {
    $('message').textContent = text;
    $('message').className = `message ${type}`;
  }

  function render() {
    $('score').textContent = game.score;
    $('wins').textContent = game.wins;
    $('losses').textContent = game.losses;
    $('best-combo').textContent = `×${game.bestCombo}`;
    $('level').textContent = game.level;
    $('combo').textContent = `×${game.combo}`;
    $('difficulty-badge').textContent = game.difficulty;
    $('current-category').textContent = game.current.category;
    $('remaining').textContent = `${game.maxAttempts - game.wrong} / ${game.maxAttempts}`;
    $('life-bar').max = game.maxAttempts;
    $('life-bar').value = game.maxAttempts - game.wrong;
    $('drawing-title').textContent = `Bamboo scaffold. ${game.wrong} wrong guesses out of ${game.maxAttempts}.`;
    const partCount = Math.ceil(game.wrong * 6 / game.maxAttempts);
    document.querySelectorAll('[data-part]').forEach((part, i) => {
      part.toggleAttribute('hidden', i >= partCount);
    });
    $('word').replaceChildren();
    const spoken = [];
    game.current.word.split(' ').forEach(word => {
      const group = document.createElement('span');
      group.className = 'word-group';
      for (const letter of word) {
        const shown = game.status !== 'playing' || game.guessed.has(letter) || !/[a-z]/.test(letter);
        const span = document.createElement('span');
        span.className = `letter${shown ? ' revealed' : ''}${letter === '-' ? ' separator' : ''}`;
        span.textContent = shown ? letter.toUpperCase() : '\u00a0';
        span.setAttribute('aria-hidden', 'true');
        spoken.push(shown ? (letter === '-' ? 'hyphen' : letter.toUpperCase()) : 'blank');
        group.append(span);
      }
      spoken.push('space');
      $('word').append(group);
    });
    spoken.pop();
    $('word').setAttribute('aria-label', `Word: ${spoken.join(', ')}`);
    keys.forEach((button, letter) => {
      const used = game.guessed.has(letter);
      const correct = game.current.word.includes(letter);
      button.disabled = used || game.status !== 'playing';
      button.className = `key${used ? correct ? ' correct' : ' wrong' : ''}`;
      button.setAttribute('aria-label', used ? `${letter.toUpperCase()}, ${correct ? 'correct' : 'incorrect'}` : `Guess ${letter.toUpperCase()}`);
    });
    $('hint').disabled = game.hintUsed || game.status !== 'playing';
    $('hint').textContent = game.hintUsed ? 'Pahiwatig used' : 'Pahiwatig −5 pts';
    $('hint-panel').hidden = !game.hintUsed;
    $('hint-text').textContent = game.hintUsed ? game.current.hint : '';
    $('result').hidden = game.status === 'playing';
    $('skip').hidden = game.status !== 'playing';
    if (game.status !== 'playing') {
      const won = game.status === 'won';
      $('result').className = `result${won ? '' : ' lost'}`;
      $('result-title').textContent = won ? 'Mahusay! You got it!' : 'Bawi sa susunod!';
      $('result-copy').textContent = `${game.current.word.toUpperCase()} — ${game.current.hint}${won ? ' +50 bonus points!' : ''}`;
    }
  }

  function guess(letter) {
    if ($('game').hidden || $('help').open || $('confirm').open) return;
    const result = game.guess(letter);
    if (result.type === 'inactive') return;
    if (result.type === 'repeat') { message(`Nahulaan mo na ang ${result.letter.toUpperCase()}. Try another letter.`); return; }
    if (result.type === 'invalid') { message('Choose a letter from A to Z.'); return; }
    if (game.status === 'won') audio.effect('victory');
    else if (game.status === 'lost') audio.effect('loss');
    else audio.effect(result.type === 'correct' ? 'correct' : 'wrong');
    render();
    if (game.status === 'won') message('MAHUSAY! You solved the word. +50 bonus points!', 'correct');
    else if (game.status === 'lost') message(`No chances left. The word was ${game.current.word.toUpperCase()}.`, 'wrong');
    else if (result.type === 'correct') message(`TAMA! Nasa salita ang ${result.letter.toUpperCase()}. +${result.gained} points`, 'correct');
    else message(`MALI! Walang ${result.letter.toUpperCase()} sa salita. ${game.maxAttempts - game.wrong} chances left.`, 'wrong');
    if (game.status !== 'playing') $('next-round').focus({ preventScroll: true });
  }

  function newRound() {
    game.next();
    render();
    message('Pumili ng letra. Guess the hidden word!');
    keys.get('q').focus({ preventScroll: true });
  }

  function confirmAction(title, copy, action) {
    pendingAction = action;
    $('confirm-title').textContent = title;
    $('confirm-copy').textContent = copy;
    $('confirm').showModal();
    $('cancel-change').focus();
  }
  $('setup').addEventListener('submit', event => {
    event.preventDefault();
    audio.activate();
    game.start($('category').value, $('difficulty').value);
    $('setup').hidden = true;
    $('game').hidden = false;
    render();
    message('Pumili ng letra. Guess the hidden word!');
    keys.get('q').focus({ preventScroll: true });
  });
  $('hint').addEventListener('click', () => {
    if (game.hint() === null) return;
    audio.effect('hint');
    render();
    message(`Pahiwatig: ${game.current.hint}`);
  });
  $('next-round').addEventListener('click', () => { audio.effect('click'); newRound(); });
  $('skip').addEventListener('click', () => confirmAction('Skip this word?', 'Your points stay, but this word and your current combo will reset.', newRound));
  $('settings').addEventListener('click', () => confirmAction('Choose a new challenge?', 'Starting a new challenge resets your points, wins, and losses.', () => {
    $('game').hidden = true;
    $('setup').hidden = false;
    $('category').focus();
  }));
  $('cancel-change').addEventListener('click', () => { pendingAction = null; $('confirm').close(); });
  $('confirm').addEventListener('cancel', () => { pendingAction = null; });
  $('confirm-change').addEventListener('click', () => {
    const action = pendingAction;
    pendingAction = null;
    $('confirm').close();
    action?.();
  });
  $('help-button').addEventListener('click', () => { audio.effect('click'); $('help').showModal(); });
  $('sound').addEventListener('click', () => audio.toggleSound());
  $('music').addEventListener('click', () => audio.toggleMusic());

  /* Music must not keep playing once the game is backgrounded — on Android the
     app stays alive behind the launcher, so without this the theme plays on. */
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) audio.suspend();
    else audio.resume();
  });
  document.addEventListener('keydown', event => {
    if (event.ctrlKey || event.altKey || event.metaKey || event.isComposing || event.repeat) return;
    if (event.target.closest('input,select,textarea,[contenteditable="true"]')) return;
    if (/^[a-z]$/i.test(event.key) && !$('game').hidden && !$('help').open && !$('confirm').open) {
      event.preventDefault();
      guess(event.key);
    }
  });
})();
