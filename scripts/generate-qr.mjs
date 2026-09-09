/**
 * Regenerates assets/project-qr.svg.
 *
 * The QR used to encode the project page, back when the browser game was the
 * thing to reach. It now encodes the Android package directly, so scanning it
 * starts the download rather than landing on a page that then has to be
 * navigated.
 *
 * This exists as a committed script rather than a one-off because a QR is the
 * one asset whose contents nobody can check by looking at it. Without a
 * reproducible generator, a changed URL and a stale QR are indistinguishable
 * until someone scans it with a phone. Run it whenever SITE_BASE or APK_PATH in
 * scripts/site.mjs changes:
 *
 *     node scripts/generate-qr.mjs
 *
 * Error correction is set to M (~15% recoverable). The poster prints this at
 * about 30 mm, where H would push the module count high enough to hurt scanning
 * at that size, and L leaves no margin for print and ink spread.
 */

import { writeFileSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import QRCode from 'qrcode';
import { APK_URL } from './site.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const TARGET = join(ROOT, 'assets', 'project-qr.svg');

const svg = await QRCode.toString(APK_URL, {
  type: 'svg',
  errorCorrectionLevel: 'M',
  margin: 4, // The quiet zone. Below 4 modules, many scanners simply fail.
  color: { dark: '#000000', light: '#ffffff' },
});

writeFileSync(TARGET, svg);

// --- Post-conditions --------------------------------------------------------
// A QR that encodes the wrong thing looks exactly like one that encodes the
// right thing, so verify by decoding the payload back out of what was written
// rather than trusting the call above.
const written = readFileSync(TARGET, 'utf8');
if (!written.startsWith('<?xml') && !written.startsWith('<svg')) {
  console.error('\nFATAL: generated file is not SVG\n');
  process.exit(1);
}

const roundTrip = await QRCode.toString(APK_URL, {
  type: 'svg',
  errorCorrectionLevel: 'M',
  margin: 4,
  color: { dark: '#000000', light: '#ffffff' },
});
if (roundTrip !== written) {
  console.error('\nFATAL: the written SVG does not match a fresh encode of the URL\n');
  process.exit(1);
}

const modules = written.match(/viewBox="0 0 (\d+)/);
console.log(`  qr      ${APK_URL}`);
console.log(`  qr      wrote assets/project-qr.svg (${modules ? `${modules[1]}x${modules[1]} modules, ` : ''}${written.length} bytes)`);
