# Containerised Android build for Hulaan Bayan.
#
# Why just and not compose:
#   docker compose cannot drive `--output type=local`, and `compose run` would
#   reintroduce the bind mount whose ownership semantics differ between rootless
#   and rootful Docker — the exact problem this setup exists to avoid.
#
# `release` contains no bind mount and no notion of which Docker mode is in use.
# See ANDROID-BUILD.md.

set shell := ["bash", "-euo", "pipefail", "-c"]

dist      := "dist"
secrets   := "secrets"
keystore  := "secrets/release.keystore"
ks_props  := "secrets/keystore.properties"
key_alias := "hulaanbayan"
apk       := "dist/hulaan-bayan-release.apk"

# Show available recipes.
default:
    @just --list --unsorted

# Signed release APK -> dist/hulaan-bayan-release.apk
release:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ ! -s "{{keystore}}" || ! -s "{{ks_props}}" ]]; then
        echo "No release keystore found. Run: just keystore" >&2
        exit 1
    fi
    mkdir -p {{dist}}
    start=$SECONDS
    docker build --target release-apk \
        --secret id=release_keystore,src={{keystore}} \
        --secret id=release_keystore_properties,src={{ks_props}} \
        --output type=local,dest={{dist}} .
    echo "--- release APK built in $((SECONDS - start))s ---"
    ls -l {{apk}}
    stat -c 'owner: %U:%G  mode: %a' {{apk}}

# Stage www/ locally, without Docker. Useful for eyeballing the link rewrites.
stage:
    node scripts/stage-www.mjs

# One-time: generate the self-managed release keystore and its properties file.
keystore:
    #!/usr/bin/env bash
    set -euo pipefail
    # Uses the host JDK's keytool when present; otherwise runs keytool in the build
    # image and captures it on stdout. Either way the file is written by this shell
    # and is therefore owned by you, in both Docker modes.
    if [[ -e "{{keystore}}" ]]; then
        echo "{{keystore}} already exists. Refusing to overwrite it." >&2
        echo "A replaced keystore cannot sign an update to an app installed with the old one." >&2
        exit 1
    fi
    mkdir -p "{{secrets}}"
    chmod 700 "{{secrets}}"

    # Non-interactive path, for CI and for agents that have no tty. The password
    # ends up in secrets/keystore.properties either way, so this reveals nothing
    # the interactive path conceals.
    if [[ -n "${HULAAN_KEYSTORE_PASSWORD:-}" ]]; then
        pw="$HULAAN_KEYSTORE_PASSWORD"
    else
        read -rsp "New keystore password (min 6 chars): " pw; echo
        read -rsp "Confirm: " pw2; echo
        [[ "$pw" == "$pw2" ]] || { echo "Passwords do not match." >&2; exit 1; }
    fi
    (( ${#pw} >= 6 )) || { echo "keytool requires at least 6 characters." >&2; exit 1; }

    dname="CN=Hulaan Bayan, OU=BSIT 1A, O=St. Francis Xavier College, L=Manila, ST=Metro Manila, C=PH"

    if command -v keytool >/dev/null 2>&1; then
        echo "Using host keytool."
        KS_PW="$pw" keytool -genkeypair -v \
            -keystore "{{keystore}}" -storetype PKCS12 \
            -alias "{{key_alias}}" -keyalg RSA -keysize 4096 -validity 10000 \
            -storepass:env KS_PW -keypass:env KS_PW -dname "$dname"
    else
        echo "No host keytool; generating inside the build image."
        docker build --target base -t hulaan-build-base . >/dev/null
        KS_PW="$pw" docker run --rm -i -e KS_PW hulaan-build-base bash -c '
            keytool -genkeypair -keystore /tmp/ks.p12 -storetype PKCS12 \
                -alias "'"{{key_alias}}"'" -keyalg RSA -keysize 4096 -validity 10000 \
                -storepass:env KS_PW -keypass:env KS_PW \
                -dname "'"$dname"'" >&2
            cat /tmp/ks.p12' > "{{keystore}}"
    fi

    umask 077
    cat > "{{ks_props}}" <<EOF
    storePassword=$pw
    keyAlias={{key_alias}}
    keyPassword=$pw
    EOF
    sed -i 's/^    //' "{{ks_props}}"
    chmod 600 "{{keystore}}" "{{ks_props}}"

    echo
    echo "Wrote {{keystore}} and {{ks_props}} (mode 600, gitignored)."
    echo "BACK THESE UP NOW — see ANDROID-BUILD.md § Keystore. Losing them is unrecoverable."
    just fingerprint

# Print the release keystore's certificate fingerprints.
fingerprint:
    #!/usr/bin/env bash
    set -euo pipefail
    # Back these up alongside the keystore: they are how you prove which key an
    # already-installed APK was signed with.
    pw=$(grep '^storePassword=' "{{ks_props}}" | cut -d= -f2-)
    if command -v keytool >/dev/null 2>&1; then
        KS_PW="$pw" keytool -list -v -keystore "{{keystore}}" \
            -alias "{{key_alias}}" -storepass:env KS_PW \
        | grep -E 'Alias|Owner|Valid from|SHA1:|SHA256:'
    else
        echo "No host keytool; run 'just verify' after a build instead." >&2
    fi

# Re-verify the signatures of whatever is in dist/.
verify:
    #!/usr/bin/env bash
    set -euo pipefail
    # Uses the container's apksigner; this host has no Android build-tools.
    docker build --target sdk -t hulaan-build-sdk . >/dev/null
    for a in {{dist}}/*.apk; do
        echo "=============== $a"
        docker run --rm -i hulaan-build-sdk \
            bash -c 'cat > /tmp/a.apk && apksigner verify --print-certs /tmp/a.apk' < "$a"
    done

# List what the APK actually bundles, to confirm the staging exclusions held.
contents:
    #!/usr/bin/env bash
    set -euo pipefail
    docker build --target sdk -t hulaan-build-sdk . >/dev/null
    docker run --rm -i hulaan-build-sdk \
        bash -c 'cat > /tmp/a.apk && unzip -l /tmp/a.apk | grep -E "assets/public|^ *Length|----" ' \
        < "{{apk}}"

# Optional interactive shell for debugging the Gradle build by hand.
shell:
    #!/usr/bin/env bash
    set -euo pipefail
    # This is the ONLY place that detects the Docker mode, and it does so precisely
    # because it is the only place that bind-mounts the source tree. `release` does
    # not go near this. Under rootless Docker container uid 0 maps to your host
    # user, so running as root produces files you own; under rootful Docker uid 0
    # is host root, so we must ask for your uid:gid instead.
    docker build --target prepared -t hulaan-build-prepared .
    # {{{{ }}}} escapes just's own interpolation, emitting literal Go-template braces.
    if docker info -f '{{{{json .SecurityOptions}}}}' | grep -q rootless; then
        echo "rootless Docker detected -> running as root (uid 0 maps to you)"
        user_args=()
    else
        echo "rootful Docker detected -> running as $(id -u):$(id -g)"
        user_args=(--user "$(id -u):$(id -g)")
    fi
    docker run --rm -it "${user_args[@]}" -w /workspace/android hulaan-build-prepared bash

# Remove built APKs and the staged web payload. Does not touch secrets/.
clean:
    rm -rf {{dist}} www

# Report what this setup costs on disk.
disk:
    #!/usr/bin/env bash
    set -euo pipefail
    docker images --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}' | grep -E 'hulaan-build' || true
    echo "--- buildx cache ---"
    docker buildx du 2>/dev/null | tail -3 || docker system df
