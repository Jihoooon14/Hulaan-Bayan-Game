# Hulaan-Bayan-Game

A Filipino word challenge built with Python and Tkinter.

The browser edition adapts the same vocabulary and rules to JavaScript for phones and computers. The original Python desktop edition remains available for the project submission.

- Open `index.html` for the project webpage.
- Open `play.html` to play in a browser; no installation, build step, or account is required.
- Open `poster.html` for the responsive poster preview, or print `downloads/Hulaan-Bayan-Poster.pdf` at 100% on 8 × 12-inch paper.
- Run `game/Hulaan-Bayan-Game/Start-Game.cmd` on Windows with Python 3 and Tkinter installed.
- The downloadable game is packaged in `downloads/Hulaan-Bayan-Game.zip`. Its editable source and bundled assets are in `game/Hulaan-Bayan-Game/`.

Project address: https://ashleyglitzjaranilla.github.io/Hulaan-Bayan-Game/

Direct play / poster QR address: https://ashleyglitzjaranilla.github.io/Hulaan-Bayan-Game/play.html

## Browser development

`assets/words.js` contains the 35 words and hints copied from the Python game's `WORD_DATA`. `assets/game-core.js` implements the same category pools, difficulties, scoring, hints, and level progression. `assets/play.js` and `assets/play.css` provide the touch and keyboard interface. Scores stay in memory for the current page session. The browser version has optional sound effects; the Python version retains its background music.

Run the rule checks with `node --test tests/game-core.test.cjs`. Serve or publish the repository as static files; `play.html` works under the GitHub Pages project path. Publish the updated QR SVG and both poster exports together with the browser files.

## Project description and desktop instructions

HULAAN BAYAN — A Filipino Word Challenge
=======================================

GAME DESCRIPTION
Hulaan Bayan is a Filipino-themed word-guessing game based on Hangman. Choose a category and difficulty, then guess one letter at a time to uncover the hidden word before your chances run out. Earn points for correct guesses, build a combo, and use a hint when you need help. With words about Filipino food, traditional games, festivals, places, culture, and heroes, each round is a chance to explore the Philippines.

GAME CONCEPT
Hulaan Bayan builds on the GROUP 5 Advanced Hangman project while keeping its familiar letter-guessing mechanics. The transformation adds Filipino vocabulary, local interface messages, Philippine-inspired colors, and a bamboo-style scaffold. The theme connects a familiar game with everyday Filipino culture and heritage. Category selection, three difficulty levels, hints, and combo scoring give this version its own identity.

FILIPINO THEME
Six categories celebrate Filipino cuisine, traditional games, festivals, destinations, cultural practices, and heroes. Blue, red, gold, a sun motif, and bamboo-inspired game artwork connect the visual identity to the Philippines.

HOW TO RUN
Install Python 3 with Tkinter support, extract the entire ZIP, then run:
    python HulaanBayan.py
On Windows, you can also double-click Start-Game.cmd.
No external pip packages are required by the game.
On Linux, your distribution may require a separate python3-tk package.
The Python desktop edition runs separately; the browser adaptation is at play.html.
Recommended display: 1280 x 800 or larger, at standard display scaling.

HOW TO PLAY
Choose a category (or all categories), then choose a difficulty.
Madali: 6 mistakes; Katamtaman: 5 mistakes; Mahirap: 4 mistakes.
Click A-Z or enter one letter and press Enter. Spaces and hyphens are shown.
Correct guesses earn 10 points plus a consecutive-correct bonus of 2 points
per additional correct letter, capped at an extra 10. Wrong guesses cost
5 points and reset the combo. Each round allows one hint costing 5 points.
Scores never fall below zero. Completing a word earns 50 bonus points.
Every two wins increases the level. Bagong Salita skips to a new word.
Starting a campaign resets scores; scores are not saved between sessions.
Windows supports synthesized sound effects; other systems use a system bell.
Windows also plays a bundled original 24-second background music loop.
MUSIKA toggles background music separately from TUNOG (sound effects).
Music plays across menus and rounds and stops when you close the game.
Background music is currently supported on Windows only.

DEVELOPERS
Names: Ashley Glitz Jaranilla; Qwyncy Eloise Caritativo; Margie Murcilla; Jaygun Bazar
Course: BSIT
Section: 1A
School: St. Francis Xavier College
Project page: https://ashleyglitzjaranilla.github.io/Hulaan-Bayan-Game/

SOURCE AND AUTHORSHIP
The supplied source identifies GROUP 5 Advanced Hangman as its starting point.
Keep the actual original game separately as evidence of the transformation.
The pre-enhancement backup in submission/ is the supplied Filipino version,
not proof of the original Hangman project. Confirm logo authorship and review
the concept statement before presenting it as your own project.
