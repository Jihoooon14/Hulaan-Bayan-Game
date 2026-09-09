/**
 * Assembles www/ — the web payload that gets bundled into the APK — from the
 * repository's own pages and assets.
 *
 * This exists as a staging step rather than pointing Capacitor's webDir at the
 * repository root for three reasons:
 *
 *   1. The app must launch into the game. Capacitor always loads
 *      webDir/index.html and has no start-page setting, so play.html has to
 *      *become* index.html, which means renaming and fixing up the links.
 *   2. Roughly 7 MB of the repository is dead weight in an APK — assets nothing
 *      references, and downloads/ archives that cannot work inside a WebView.
 *   3. GitHub Pages serves the repository root as-is. Rewriting files in place
 *      would break the published site, so every edit happens on the copy.
 *
 * Nothing here mutates the repository. Input is read, output goes to www/.
 *
 * Every rewrite asserts how many occurrences it expects to find and fails the
 * build on a mismatch. A future edit that adds, removes or renames a cross-page
 * link therefore fails loudly here instead of shipping an APK with a link that
 * dead-ends or loops back to the game.
 */

import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync, readdirSync, statSync } from 'node:fs';
import { join, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const WWW = join(ROOT, 'www');

/** Where the real downloads live, since they cannot be served from inside the APK. */
const PAGES_BASE = 'https://jihoooon14.github.io/Hulaan-Bayan-Game';

/**
 * Assets deliberately left out.
 *
 * bayan-theme.wav is the uncompressed 24-second theme: mono 22.05 kHz PCM, 1.01 MB
 * for audio that AAC carries in 179 KB. play.html loads bayan-theme.m4a instead,
 * so the WAV is unreachable from any page. It stays in the repository because the
 * Python desktop game needs PCM for winsound — that copy lives under
 * game/Hulaan-Bayan-Game/assets/ and this never touches it.
 */
const EXCLUDED_ASSETS = new Set(['bayan-theme.wav']);

/**
 * play.html becomes the launch page, so the landing page has to move aside.
 * Order matters: these renames invert the meaning of `index.html`, which is why
 * the link rewrites below are applied per-file and never as a global pass.
 */
const PAGES = [
  { from: 'play.html', to: 'index.html' },
  { from: 'index.html', to: 'about.html' },
  { from: 'poster.html', to: 'poster.html' },
];

/** A download that has to leave the app to work. */
const download = (page, file, count) => [
  page,
  `href="downloads/${file}"`,
  `href="${PAGES_BASE}/downloads/${file}"`,
  count,
];

/** [staged filename, literal to replace, replacement, exact expected count] */
const REWRITES = [
  // --- Cross-page navigation, fixed up for the rename ---------------------
  // The game's header links back to the project page, which is now about.html.
  ['index.html', 'href="index.html"', 'href="about.html"', 2],
  ['index.html', 'href="index.html#developers"', 'href="about.html#developers"', 1],

  // The landing page's play links now point at the launch page.
  ['about.html', 'href="play.html"', 'href="index.html"', 2],

  // The poster page links to the game by absolute URL, which under Capacitor
  // would be treated as off-app and opened in the system browser — pushing the
  // user out to the website to play a game they already have installed. Made
  // relative so navigation stays inside the app.
  [
    'poster.html',
    `href="${PAGES_BASE}/play.html"`,
    'href="index.html"',
    1,
  ],

  // --- Downloads ----------------------------------------------------------
  // A relative <a href> to a bundled file does not trigger Android's download
  // manager under Capacitor's scheme, so these would be dead inside the app
  // whether or not downloads/ were bundled. Sending them to the published site
  // instead makes them work: Capacitor's shouldOverrideUrlLoading fires an
  // ACTION_VIEW intent for http(s) URLs outside the app's scope, so they open in
  // the system browser and download normally. No Capacitor plugin is involved.
  download('index.html', 'Hulaan-Bayan-Game.zip', 2),
  download('about.html', 'Hulaan-Bayan-Game.zip', 2),
  download('about.html', 'Hulaan-Bayan-Poster.pdf', 1),
  download('poster.html', 'Hulaan-Bayan-Poster.pdf', 1),
  download('poster.html', 'Hulaan-Bayan-Poster.png', 1),
];

const fail = (message) => {
  console.error(`\nFATAL: ${message}\n`);
  process.exit(1);
};

// --- Clean, so a removed source file cannot survive in a stale www/. ---------
rmSync(WWW, { recursive: true, force: true });
mkdirSync(WWW, { recursive: true });

// --- Pages ------------------------------------------------------------------
const staged = new Map();
for (const { from, to } of PAGES) {
  const source = join(ROOT, from);
  try {
    staged.set(to, readFileSync(source, 'utf8'));
  } catch {
    fail(`expected page ${from} is missing from the repository root`);
  }
  console.log(`  page    ${from}  ->  www/${to}`);
}

// --- Link rewrites ----------------------------------------------------------
for (const [page, needle, replacement, expected] of REWRITES) {
  const before = staged.get(page);
  if (before === undefined) fail(`rewrite targets www/${page}, which is not staged`);

  const found = before.split(needle).length - 1;
  if (found !== expected) {
    fail(
      `www/${page}: expected ${expected} occurrence(s) of ${needle}, found ${found}.\n` +
        `       The page changed. Update REWRITES in scripts/stage-www.mjs to match,\n` +
        `       or the APK will ship a broken link.`
    );
  }

  staged.set(page, before.split(needle).join(replacement));
  console.log(`  rewrite www/${page}: ${needle} -> ${replacement}  (${found})`);
}

for (const [name, contents] of staged) writeFileSync(join(WWW, name), contents);

// --- Assets -----------------------------------------------------------------
mkdirSync(join(WWW, 'assets'), { recursive: true });
let copied = 0;
let skipped = 0;
for (const entry of readdirSync(join(ROOT, 'assets'))) {
  if (EXCLUDED_ASSETS.has(entry)) {
    console.log(`  skip    assets/${entry}  (unreachable from any page)`);
    skipped += 1;
    continue;
  }
  cpSync(join(ROOT, 'assets', entry), join(WWW, 'assets', entry), { recursive: true });
  copied += 1;
}

if (skipped !== EXCLUDED_ASSETS.size) {
  fail(
    `expected to skip ${EXCLUDED_ASSETS.size} asset(s), skipped ${skipped}.\n` +
      `       An excluded asset was renamed or deleted; update EXCLUDED_ASSETS.`
  );
}

// --- Post-conditions --------------------------------------------------------
// Assert against the staged output rather than trusting the rewrites above, so
// a link introduced by a page this script does not know about is still caught.
const stagedPages = [...staged.keys()];
for (const page of stagedPages) {
  const contents = readFileSync(join(WWW, page), 'utf8');

  if (contents.includes('href="play.html"')) {
    fail(`www/${page} still links to play.html, which does not exist in the APK`);
  }
  if (/href="(?!https?:)[^"]*downloads\//.test(contents)) {
    fail(
      `www/${page} still has a relative downloads/ link.\n` +
        `       Relative download links do not work inside the WebView. Add it to\n` +
        `       REWRITES in scripts/stage-www.mjs so it points at ${PAGES_BASE}.`
    );
  }
}

// The launch page must be the game, not the landing page.
const launch = readFileSync(join(WWW, 'index.html'), 'utf8');
if (!launch.includes('id="keyboard"')) {
  fail('www/index.html is not the game page — the play.html -> index.html rename did not take');
}

// --- Report -----------------------------------------------------------------
const bytes = (dir) =>
  readdirSync(dir, { withFileTypes: true }).reduce((total, e) => {
    const p = join(dir, e.name);
    return total + (e.isDirectory() ? bytes(p) : statSync(p).size);
  }, 0);

const total = bytes(WWW);
console.log(
  `\n  staged ${stagedPages.length} page(s) and ${copied} asset(s) into ` +
    `${relative(ROOT, WWW)}/  (${(total / 1024 / 1024).toFixed(2)} MB)\n`
);
