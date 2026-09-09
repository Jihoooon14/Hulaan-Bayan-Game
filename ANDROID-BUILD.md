# Building the Hulaan Bayan Android APK

The Android app is the **browser edition** of the game — `play.html` and
`assets/` — wrapped by [Capacitor](https://capacitorjs.com) in a native shell.
The whole game runs offline from files bundled inside the APK. No server, no
account, no internet connection needed to play.

> **The Python desktop game is not what gets built here, and cannot be.**
> `game/Hulaan-Bayan-Game/HulaanBayan.py` is a Tkinter application, and no
> Android toolchain ships Tk — not python-for-android/Buildozer, not BeeWare
> Briefcase, not Chaquopy. Tk needs an X11, Win32 or Cocoa windowing layer that
> Android does not provide. The Python edition remains the desktop game and is
> untouched by any of this.

| Artifact | Command | Lands at |
|---|---|---|
| Signed release APK | `just release` | `dist/hulaan-bayan-release.apk` |

---

## 1. Prerequisites

- **Docker with BuildKit**, rootless or rootful — see §6, the setup does not
  care which. Verified against Docker 29.7.2 rootless with the default `docker`
  buildx driver.
- **`just`** on the host.
- **Disk**: roughly 4 GB. See §7.

Nothing else. No Android Studio, no `sdkmanager`, no Android SDK, no JDK on the
host. `adb` is needed only to *install* the result — §5.

This matters on NixOS in particular, where the Android SDK's prebuilt glibc
binaries (`aapt2`, `d8`, `apksigner`) need `nix-ld` or `patchelf` to run at all.
Building in a container removes that question entirely.

---

## 2. Quick start

```bash
just keystore     # once, ever
just release
```

`just release` refuses to run without `secrets/release.keystore`.

---

## 3. What actually goes into the APK

The APK does not bundle the repository as-is. `scripts/stage-www.mjs` assembles
a `www/` directory first, and the Docker build runs it. Nothing in the repository
is modified — GitHub Pages keeps serving exactly what it serves today, and every
edit happens on the staged copy.

### 3.1 Pages are renamed so the app launches into the game

Capacitor always loads `webDir/index.html` at startup and has no start-page
setting, so launching into the game is a rename, not a configuration option:

| Repository file | Staged as | Role in the app |
|---|---|---|
| `play.html` | `www/index.html` | launch page — the game |
| `index.html` | `www/about.html` | project landing page |
| `poster.html` | `www/poster.html` | unchanged |

The cross-page links are rewritten to match. `stage-www.mjs` asserts the exact
number of occurrences it expects to find for every rewrite and fails the build on
a mismatch, so editing a page in a way that invalidates the link map fails loudly
here rather than shipping an APK whose "About the project" link loops back to the
game.

### 3.2 Download links leave the app

A relative `<a href="downloads/...">` does not trigger Android's download manager
under Capacitor's scheme, so those links are dead inside a WebView whether or not
the files are bundled. All five are rewritten to absolute
`https://jihoooon14.github.io/Hulaan-Bayan-Game/downloads/...` URLs.

Capacitor's `shouldOverrideUrlLoading` fires an `ACTION_VIEW` intent for http(s)
URLs outside the app's scope, so they open in the system browser and download
normally. This needs no Capacitor plugin — the app has **zero** native plugins.

`poster.html`'s absolute link *back* to the game is rewritten in the opposite
direction, to a relative `index.html`, so tapping it does not eject the user to
the website to play a game they already have installed.

### 3.3 What is left out

| Excluded | Size | Reason |
|---|---|---|
| `assets/game-audio.js` | 5.4 KB | Dead. No HTML file in the repository references it. |
| `assets/bayan-theme.wav` | 1.1 MB | Dead on web. Only `game-audio.js` would load it, and nothing loads that. The Python game's own copy under `game/Hulaan-Bayan-Game/assets/` is untouched. |
| `downloads/` | 9.2 MB | Cannot work as relative links (§3.2). `Hulaan-Bayan-Website.zip` is not linked from anywhere at all. |

Bundled payload: **~1.26 MB**, down from ~11.5 MB.

Sound still works. The game synthesises its effects in-process through the Web
Audio API (`assets/play.js:33`); it never loads an audio file.

---

## 4. Signing, and why a mis-signed APK cannot slip through

### 4.1 How the wiring works

`android/` is generated output and is gitignored, so a hand-edit to
`android/app/build.gradle` would be destroyed by the next `npx cap add android`.
`scripts/apply-android-config.mjs` re-applies the wiring on every build instead.

It follows Expo's EAS integration approach: write a self-contained
`android/app/hulaan-bayan.gradle` and append one `apply from:` line to
`build.gradle`. Appending a line is stable across Capacitor template changes;
regex-editing the `android { }` block is not. The script is idempotent.

Credentials never pass through the script, through `capacitor.config.json`, or
through any generated file. The emitted Gradle reads two environment variables
holding **paths**:

| Variable | Points at |
|---|---|
| `HULAAN_RELEASE_KEYSTORE` | `/run/secrets/release.keystore` |
| `HULAAN_RELEASE_KEYSTORE_PROPERTIES` | `/run/secrets/keystore.properties` |

Both are BuildKit **secret mounts**, present only for the duration of the single
`RUN` that assembles the release build. They are not in any image layer, not in
`docker history`, not in `ARG` or `ENV`, and the passwords are never in an
environment variable or on a command line — the Gradle script loads them from the
properties file at execution time.

If those variables are unset the wiring stands down, so a local
`gradlew assembleRelease` still works on a machine with no keystore.

The same file also sets `versionCode` and `versionName`, which Capacitor does not
take from `capacitor.config.json` and which would otherwise be the template's
`1` / `"1.0"`.

### 4.2 The gates

Capacitor's template sets **no `signingConfig` on the release build type at
all**. If the signing wiring fails to apply, `assembleRelease` still succeeds —
it just emits `app-release-unsigned.apk` instead of `app-release.apk`. That is
louder than Expo's silent debug-key fallback, but it is not self-explanatory, and
a future template could add a fallback. The build therefore has three gates, any
of which fails it:

1. **Wiring gate**, in the `prepared` stage: `hulaan-bayan.gradle` exists and
   `build.gradle` applies it. Cheap to discover here, expensive after a full
   build.
2. **Marker gate**: `hulaan-bayan.gradle` logs
   `HULAAN-SIGNING: release keystore active` at Gradle lifecycle level when it
   actually takes. The build greps the Gradle log for it.
3. **Certificate gate**: `apksigner verify --print-certs` runs on the produced
   APK. The build fails if the signer is `CN=Android Debug`, and equally if
   `apksigner` reports no signer certificate.

A fourth check asserts that the APK's launch page is the game, by grepping the
bundled `assets/public/index.html` for the keyboard element.

To re-check the artifacts later:

```bash
just verify        # apksigner, in the container, against everything in dist/
just fingerprint   # the release keystore's own SHA-1/SHA-256
just contents      # what the APK actually bundles
```

---

## 5. Installing on the phone

**`adb` runs on the host, not in the container.** USB passthrough into rootless
Docker is not worth the trouble, so the container never sees the device.

### 5.1 Get `adb`

On NixOS, without touching system config:

```bash
nix-shell -p android-tools
```

On other distros install `android-tools` (Debian/Ubuntu: `android-tools-adb`).

### 5.2 udev rules — you must do this yourself

Plugging in a phone also needs udev rules, or `adb devices` shows the device as
`no permissions`. On NixOS that means editing `/etc/nixos/configuration.nix`:

```nix
programs.adb.enable = true;
users.users.<you>.extraGroups = [ "adbusers" ];
```

then `sudo nixos-rebuild switch`, then log out and back in for the group to take
effect.

**This needs sudo and your password, so do it yourself — the build tooling does
not attempt it.** On other distros the equivalent is installing
`android-udev-rules` and adding yourself to `plugdev`.

### 5.3 Install

On the phone: Settings → About → tap Build number seven times → Developer
options → enable **USB debugging**. Plug in, accept the RSA prompt.

```bash
adb devices                                    # confirm 'device', not 'unauthorized'
adb install -r dist/hulaan-bayan-release.apk
```

### 5.4 Installing without a computer

For handing the APK to classmates, `adb` is not involved at all. Copy the `.apk`
to the phone (USB, Drive, messaging app) and tap it. Android will ask permission
to install from that source; on Android 8+ this is granted per-app, to whichever
app is doing the handing over — Files, Chrome, Drive.

Because the APK is signed with a self-managed key rather than distributed through
Play, Play Protect will show a warning. That is expected for a sideloaded app and
is not a sign anything is wrong with the build.

---

## 6. Why this setup is Docker-mode-agnostic

The requirement: identical behaviour under rootless and rootful Docker, on any
machine, with no per-machine configuration.

Under **rootless** Docker, container uid 0 maps through a user namespace to the
invoking host user — a container running as root writes files the host user owns.
Under **rootful** Docker, container uid 0 *is* host root, and the same run writes
root-owned files into the repository. So no single `--user` value is correct for
both.

**File ownership on the host is only ever a question for bind mounts.** Remove
them from the build path and the problem does not exist:

| Concern | Mechanism | Why ownership never arises |
|---|---|---|
| Gradle and bun caches | `RUN --mount=type=cache` | Docker-managed storage inside the daemon's data dir. Not a host path. |
| Android SDK | An ordinary image layer | Lives in the image. A source change never re-downloads it, and it survives `docker builder prune`, which a cache mount does not. |
| Keystore and passwords | `RUN --mount=type=secret` | Injected into one `RUN`, never written to a layer. |
| Getting the APK out | `FROM scratch` stage + `--output type=local` | BuildKit's local exporter writes the file itself, as the user who invoked `docker build`. |

`just release` contains no `-v`, no `--mount`, no `--user` and no mode detection.
`just shell` is the one exception — an optional interactive shell for poking at
Gradle by hand, and the only recipe that bind-mounts, so the only one that
detects the mode. Nothing it does can affect what `just release` produces.

---

## 7. What it costs on disk

Run `just disk` for current numbers. Roughly:

| | Size |
|---|---|
| `sdk` stage layers (SDK 36, build-tools 36.0.0) | ~2.5 GB |
| JS dependencies, staged assets, generated `android/` | ~0.5 GB |
| BuildKit cache mounts (Gradle, bun) after a warm build | ~1 GB |

Far smaller than an equivalent React Native build, which additionally needs the
NDK and CMake (~3.5 GB more) because its dependencies compile C++. A Capacitor
app with no native plugins compiles none, so neither is installed.

The build `RUN` deletes `android/app/build` in the same layer after copying the
APK to `/out`, so the build layer does not carry intermediates.

To reclaim space: `docker buildx prune` drops the cache mounts (the next build
re-downloads Gradle dependencies but **not** the SDK, which is an image layer).

---

## 8. Layering, and what a rebuild redoes

```
base        JDK 21 · Node 22.23.2 · bun 1.3.13     keyed on: Dockerfile
  ↓
sdk         SDK 36 · build-tools 36.0.0            keyed on: Dockerfile
  ↓
deps        bun install --frozen-lockfile          keyed on: package.json, bun.lock
  ↓
staged      scripts/stage-www.mjs -> www/          keyed on: scripts/, *.html, assets/
  ↓
prepared    npx cap add android + apply-android-config
                                                   keyed on: capacitor.config.json
  ↓
build-release   gradlew assembleRelease
  ↓
release-apk     FROM scratch — APK only
```

Editing a page or an asset invalidates `staged` downward. Only editing the
`Dockerfile` re-downloads the SDK.

### Pinned versions

| Component | Version | Established from |
|---|---|---|
| Capacitor | 8.5.1 | `package.json` |
| `compileSdk` / `targetSdk` / `minSdk` | 36 / 36 / 24 | Capacitor's `android-template/variables.gradle` |
| Android Gradle Plugin | 8.13.0 | `@capacitor/android/capacitor/build.gradle` |
| Gradle | 8.14.3 | template `gradle-wrapper.properties` |
| JDK | 21 | `@capacitor/android`'s own `compileOptions` (source/target 21) |
| Android build-tools | 36.0.0 | matches `compileSdk` 36 |
| Node / bun | 22.23.2 / 1.3.13 | `Dockerfile` ARGs |

`minSdk 24` means Android 7.0 and above.

---

## 9. Keystore handling and loss recovery

`just keystore` generates a **self-managed** keystore, deliberately not a
Play-managed one, so nothing about signing depends on a cloud account.

```
secrets/                    # mode 700, gitignored
  release.keystore          # PKCS12, RSA 4096, 10000 days, alias "hulaanbayan"
  keystore.properties       # storePassword / keyAlias / keyPassword
```

Both are mode 600 and covered by `.gitignore` (`/secrets/`, plus `*.keystore`,
`*.p12`, `*.jks`, `keystore.properties` as belt-and-braces). They reach the build
only through `--mount=type=secret`.

**The password is stored in plaintext in `secrets/keystore.properties`.** That is
a deliberate choice, taken so `just release` runs unattended. It is the same
posture as `android/app/debug.keystore`, and it is a real exposure: anyone who
can read your home directory can sign as you. If that stops being acceptable,
`just release` reads the file at invocation, so a password-manager shim (`pass`,
`age`, a keychain) can materialise it into a temp file first without any change
to the Dockerfile.

### Back it up now

```bash
just fingerprint     # record this output alongside the backup
```

Copy `secrets/` somewhere durable and off this machine — a password manager
attachment or an encrypted archive. Record the SHA-256 fingerprint separately: it
is how you later prove which key an already-installed APK was signed with.

### If the keystore is lost

There is **no recovery**. The key is not derivable from the APK, from the
password, or from anything else. Android identifies an app by
`(applicationId, signing key)`, so:

- You cannot ship an update to any device that has the old APK installed.
  Installing a new-key build over it fails with
  `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.
- The only path forward is `just keystore` again after deleting `secrets/`, then
  **uninstalling the old app on every device** before installing the new one.

`just keystore` refuses to overwrite an existing keystore for exactly this reason.

If this ever goes to the Play Store the calculus changes: Play App Signing holds
the app signing key, and a lost *upload* key can be reset through support. That
is out of scope here — this setup produces a sideloadable APK, not an `.aab`.

---

## 10. Known gaps

- **App icon is Capacitor's default.** `assets/logo.png` exists but is a 1.2 MB
  PNG with no adaptive-icon foreground/background split. Generating a proper
  icon set (`mipmap-*dpi`, adaptive foreground/background, monochrome) is
  separate work.
- **No `.aab`.** `assembleRelease` produces an APK for sideloading. Play Store
  submission would need `bundleRelease` and a different signing posture (§9).
- **Not verified on a physical device.** The build and its signature are verified
  by the gates in §4.2; actually installing it needs `adb` and udev rules, which
  need sudo (§5.2).
