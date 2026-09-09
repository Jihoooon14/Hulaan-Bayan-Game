# syntax=docker/dockerfile:1.7
#
# Containerised Android build for Hulaan Bayan.
#
# The game is the existing browser port (play.html + assets/), wrapped by
# Capacitor. Nothing here compiles native code, so unlike a React Native build
# this needs no NDK and no CMake — just the SDK, build-tools and a JDK.
#
# The defining constraint, inherited from the geotagger build this is modelled
# on, is that it must behave identically under rootless and rootful Docker with
# no per-machine configuration. That is achieved by having no bind mounts
# anywhere in the build path — file ownership on the host is only ever a question
# for bind mounts. Caches are BuildKit cache mounts, credentials are BuildKit
# secret mounts, and the APK leaves via a `FROM scratch` stage exported with
# `--output type=local`, which BuildKit writes as the invoking user in both
# modes. See ANDROID-BUILD.md.
#
# Layering is ordered so that editing a page or an asset re-runs only staging and
# Gradle: the ~2.5 GB Android SDK layer is keyed on this file alone.

ARG JDK_IMAGE=eclipse-temurin:21-jdk-noble

# ---------------------------------------------------------------------------
# base — JDK 21, Node 22 and bun.
#
# JDK 21 is required, not merely preferred. @capacitor/android 8.5.1 compiles
# itself at source/target 21 — see node_modules/@capacitor/android/capacitor/
# build.gradle compileOptions, and the generated android/app/capacitor.build.gradle
# which repeats it for the app module. JDK 17 satisfies AGP 8.13.0's own minimum
# but fails this build with:
#     error: invalid source release: 21
# during :capacitor-android:compileReleaseJavaWithJavac.
# ---------------------------------------------------------------------------
FROM ${JDK_IMAGE} AS base

# Fail fast and let `cmd | tee log` propagate cmd's exit status.
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

ARG NODE_VERSION=22.23.2
ARG BUN_VERSION=1.3.13

ENV DEBIAN_FRONTEND=noninteractive \
    CI=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl unzip git xz-utils \
 && rm -rf /var/lib/apt/lists/*

# Node from the official tarball rather than a distro package, so the version is
# pinned exactly and does not drift with the base image.
RUN curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" -o /tmp/node.tar.xz \
 && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" -o /tmp/SHASUMS256.txt \
 && (cd /tmp && grep " node-v${NODE_VERSION}-linux-x64.tar.xz\$" SHASUMS256.txt | sed 's| .*/| |' > node.sha256 \
     && sed -i "s|node-v${NODE_VERSION}-linux-x64.tar.xz|node.tar.xz|" node.sha256 \
     && sha256sum -c node.sha256) \
 && mkdir -p /opt/node \
 && tar -xJf /tmp/node.tar.xz -C /opt/node --strip-components=1 \
 && rm -f /tmp/node.tar.xz /tmp/SHASUMS256.txt /tmp/node.sha256
ENV PATH=/opt/node/bin:${PATH}

# bun pinned to the version that produced bun.lock, so --frozen-lockfile is honest.
RUN curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v${BUN_VERSION}/bun-linux-x64.zip" -o /tmp/bun.zip \
 && unzip -q /tmp/bun.zip -d /tmp/bun \
 && install -m 0755 /tmp/bun/bun-linux-x64/bun /usr/local/bin/bun \
 && rm -rf /tmp/bun /tmp/bun.zip \
 && bun --version

# ---------------------------------------------------------------------------
# sdk — Android SDK and build-tools.
#
# Deliberately a real image layer, not a cache mount: a source change must never
# re-download these, and a layer survives `docker builder prune` whereas a cache
# mount does not.
#
# Versions come from the Capacitor 8.5.1 android template
# (assets/android-template/variables.gradle: compileSdk 36, targetSdk 36,
# minSdk 24). No NDK and no CMake: a Capacitor app with no native plugins
# compiles no C++, which is the bulk of what a React Native build needs.
# ---------------------------------------------------------------------------
FROM base AS sdk

ARG CMDLINE_TOOLS_VERSION=13114758
# SHA-1 is what Google publishes for this artifact in repository2-3.xml; this is
# an integrity check against a truncated or swapped download, not a security
# boundary (TLS is that).
ARG CMDLINE_TOOLS_SHA1=5fdcc763663eefb86a5b8879697aa6088b041e70

ARG ANDROID_COMPILE_SDK=36
ARG ANDROID_BUILD_TOOLS=36.0.0

ENV ANDROID_HOME=/opt/android-sdk \
    ANDROID_SDK_ROOT=/opt/android-sdk
ENV ANDROID_BUILD_TOOLS_VERSION=${ANDROID_BUILD_TOOLS}
ENV PATH=${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/build-tools/${ANDROID_BUILD_TOOLS}:${PATH}

RUN curl -fsSL "https://dl.google.com/android/repository/commandlinetools-linux-${CMDLINE_TOOLS_VERSION}_latest.zip" -o /tmp/cmdline-tools.zip \
 && echo "${CMDLINE_TOOLS_SHA1}  /tmp/cmdline-tools.zip" | sha1sum -c - \
 && mkdir -p "${ANDROID_HOME}/cmdline-tools" \
 && unzip -q /tmp/cmdline-tools.zip -d /tmp/cmdline-tools \
 && mv /tmp/cmdline-tools/cmdline-tools "${ANDROID_HOME}/cmdline-tools/latest" \
 && rm -rf /tmp/cmdline-tools.zip /tmp/cmdline-tools

# NB: `yes | sdkmanager` would fail here. sdkmanager stops reading once the
# licences are accepted, `yes` takes SIGPIPE and exits 141, and this stage's
# SHELL sets `pipefail`. A bounded, finite input avoids the broken pipe entirely.
RUN printf 'y\n%.0s' $(seq 1 50) | sdkmanager --licenses > /dev/null \
 && sdkmanager --install \
      "platform-tools" \
      "platforms;android-${ANDROID_COMPILE_SDK}" \
      "build-tools;${ANDROID_BUILD_TOOLS}" \
 && rm -rf "${ANDROID_HOME}/.temp" /root/.android/cache \
 && rm -rf "${ANDROID_HOME}/emulator" \
 && du -sh "${ANDROID_HOME}"

# ---------------------------------------------------------------------------
# deps — JS dependencies. Keyed on the lockfile, so editing a page does not
#        reinstall.
# ---------------------------------------------------------------------------
FROM sdk AS deps
WORKDIR /workspace

# ImageMagick renders the launcher icons in the `prepared` stage. Installed here
# rather than in `base` so that adding it cannot invalidate the ~2.5 GB sdk layer.
#
# Noble ships ImageMagick 6, which provides `convert` and `identify` but no
# unified `magick` binary — that arrived in ImageMagick 7. scripts/generate-icons.sh
# resolves whichever is present, so it runs here and on a developer machine alike.
RUN apt-get update \
 && apt-get install -y --no-install-recommends imagemagick \
 && rm -rf /var/lib/apt/lists/* \
 && convert -version | head -1

# bun ships bunx as a symlink to itself; installing the bare binary skips it.
# Added here rather than in `base` so it cannot invalidate the ~2.5 GB sdk layer.
RUN ln -sf /usr/local/bin/bun /usr/local/bin/bunx

COPY package.json bun.lock ./
RUN --mount=type=cache,target=/root/.bun/install/cache,sharing=locked \
    bun install --frozen-lockfile

# ---------------------------------------------------------------------------
# staged — assemble www/ from the repository's pages and assets.
#
# The staging script renames play.html to index.html so the app launches into
# the game, rewrites the cross-page and download links to match, and drops the
# assets nothing references. Every rewrite asserts its expected occurrence count,
# so a page edit that invalidates the link map fails here rather than shipping a
# broken link.
# ---------------------------------------------------------------------------
FROM deps AS staged
COPY scripts ./scripts
COPY index.html play.html poster.html ./
COPY assets ./assets
RUN node scripts/stage-www.mjs

# ---------------------------------------------------------------------------
# prepared — generate android/ from capacitor.config.json.
#
# android/ is generated output and is gitignored, so it is regenerated here
# rather than copied in. That keeps the build reproducible from a fresh clone and
# makes it impossible for a hand-edit to android/ to survive. The signing and
# version wiring is re-applied on every build by scripts/apply-android-config.mjs.
# ---------------------------------------------------------------------------
FROM staged AS prepared
COPY capacitor.config.json ./

RUN npx cap add android \
 && node scripts/apply-android-config.mjs \
 && ./scripts/generate-icons.sh

# Verify the config script actually took. Cheap here; expensive to discover
# after a full release build.
RUN test -f android/app/hulaan-bayan.gradle \
 && grep -q 'apply from: "./hulaan-bayan.gradle"' android/app/build.gradle \
 || { echo "FATAL: apply-android-config.mjs did not wire android/app/build.gradle"; exit 1; }

# Assert the staged web payload actually reached the native project, and that the
# launch page is the game rather than the landing page.
RUN test -f android/app/src/main/assets/public/index.html \
 && grep -q 'id="keyboard"' android/app/src/main/assets/public/index.html \
 || { echo "FATAL: the APK's launch page is not the game"; exit 1; }

# The background music must actually be in the payload, and must be the compressed
# track rather than the 1 MB WAV the staging step drops.
RUN test -f android/app/src/main/assets/public/assets/bayan-theme.m4a \
 && test ! -f android/app/src/main/assets/public/assets/bayan-theme.wav \
 && grep -q 'id="music-track"' android/app/src/main/assets/public/index.html \
 || { echo "FATAL: background music is missing from the APK payload"; exit 1; }

# `npx cap add android` restores Capacitor's default Ionic logo on every build, so
# a silently skipped icon step would ship that instead of the project logo.
RUN test -s android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_foreground.png \
 && grep -q '0B1F3A' android/app/src/main/res/values/ic_launcher_background.xml \
 || { echo "FATAL: launcher icons were not applied"; exit 1; }

# -XX:-UsePerfData is not a tuning knob, it is a crash fix. The JVM mmaps a
# perf-counter file under /tmp/hsperfdata_*; when the filesystem behind it runs
# out of space, the next write to that mapping raises SIGBUS and the JVM aborts
# mid-build with "SIGBUS ... PerfLongVariant::sample()" rather than any sensible
# disk-full error. Nothing here reads those counters, so turn them off.
ARG GRADLE_MAX_WORKERS=4
RUN printf '%s\n' \
      '' \
      '# --- appended by the containerised build; see Dockerfile ---' \
      'org.gradle.jvmargs=-Xmx3g -XX:MaxMetaspaceSize=1g -XX:-UsePerfData' \
      "org.gradle.workers.max=${GRADLE_MAX_WORKERS}" \
      >> android/gradle.properties \
 && tail -4 android/gradle.properties

ENV GRADLE_USER_HOME=/root/.gradle

# ---------------------------------------------------------------------------
# build-release — signed release APK.
#
# The keystore and its passwords arrive as secret mounts: present only for the
# duration of this RUN, never written to a layer, never in ARG/ENV, never in
# `docker history`. The Gradle side is scripts/apply-android-config.mjs, which
# reads the *paths* below and loads the passwords from the properties file.
# ---------------------------------------------------------------------------
FROM prepared AS build-release
RUN --mount=type=cache,target=/root/.gradle,sharing=locked \
    --mount=type=secret,id=release_keystore,target=/run/secrets/release.keystore \
    --mount=type=secret,id=release_keystore_properties,target=/run/secrets/keystore.properties <<'BUILD'
export HULAAN_RELEASE_KEYSTORE=/run/secrets/release.keystore
export HULAAN_RELEASE_KEYSTORE_PROPERTIES=/run/secrets/keystore.properties

test -s "${HULAAN_RELEASE_KEYSTORE}" || {
  echo "FATAL: release keystore secret is empty or missing. Run: just keystore"; exit 1; }

cd /workspace/android
./gradlew --no-daemon --build-cache assembleRelease 2>&1 | tee /tmp/gradle-release.log

# --- Gate 1: did the signing config actually take? ------------------------
# Capacitor's template sets no signingConfig on the release build type at all,
# so wiring that fails to apply yields app-release-unsigned.apk. That is louder
# than Expo's debug-key fallback, but it is not self-explanatory, and a future
# template could add a fallback. Check explicitly.
grep -q 'HULAAN-SIGNING: release keystore active' /tmp/gradle-release.log || {
  echo "FATAL: release signing config did not apply; the APK would be unsigned."
  grep 'HULAAN-SIGNING' /tmp/gradle-release.log || echo "(no HULAAN-SIGNING marker at all)"
  exit 1; }

mkdir -p /out
cp app/build/outputs/apk/release/app-release.apk /out/hulaan-bayan-release.apk

apksigner verify --print-certs /out/hulaan-bayan-release.apk | tee /tmp/certs.txt

# --- Gate 2: prove the signer is neither absent nor the debug key ----------
if grep -qi 'CN=Android Debug' /tmp/certs.txt; then
  echo "FATAL: release APK is signed with the Android debug key."
  exit 1
fi
grep -q 'Signer #1 certificate DN' /tmp/certs.txt || {
  echo "FATAL: apksigner reported no signer certificate; the APK is unsigned."
  exit 1; }
echo "OK: release APK is signed with a non-debug certificate."

# Drop the intermediates inside the same layer.
rm -rf /workspace/android/app/build /workspace/android/build /workspace/android/.gradle
BUILD

# ---------------------------------------------------------------------------
# Export stage. `FROM scratch` so the exported directory contains the APK and
# nothing else. BuildKit's local exporter writes it as the invoking user under
# both rootless and rootful Docker.
# ---------------------------------------------------------------------------
FROM scratch AS release-apk
COPY --from=build-release /out/ /
