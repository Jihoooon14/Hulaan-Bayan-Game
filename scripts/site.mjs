/**
 * The one place the project's published address is written down.
 *
 * Two things need an absolute URL and must never disagree: the QR code
 * (scanned off a screen or a printed poster, where nothing relative can
 * resolve) and the download links inside the APK (a relative href under
 * Capacitor's scheme cannot reach a file the app does not bundle). Everything
 * else on the site stays relative, which is why the pages already work
 * unmodified from any origin they are served from.
 *
 * The project is published from more than one GitHub account. Only the
 * canonical origin below actually serves play.html and the APK today; the
 * mirror is listed so the set is written down rather than remembered. To
 * switch canonical origins, change CANONICAL here and re-run:
 *
 *     node scripts/generate-qr.mjs
 *
 * or override for one build without editing anything:
 *
 *     HULAAN_SITE_BASE=https://example.github.io/Hulaan-Bayan-Game node scripts/stage-www.mjs
 */

/** Origins the project is published from. The first is canonical. */
export const ORIGINS = [
  'https://jihoooon14.github.io/Hulaan-Bayan-Game',
  'https://ashleyglitzjaranilla.github.io/Hulaan-Bayan-Game',
];

/**
 * The origin baked into the QR code and into the APK's own links.
 *
 * Trailing slashes are stripped so callers can always join with a leading '/'.
 */
export const SITE_BASE = (process.env.HULAAN_SITE_BASE || ORIGINS[0]).replace(/\/+$/, '');

/** The Android package, as served by the canonical origin. */
export const APK_PATH = '/downloads/Hulaan-Bayan-Android.apk';

/** Absolute URL of the Android package — what the QR encodes. */
export const APK_URL = `${SITE_BASE}${APK_PATH}`;
