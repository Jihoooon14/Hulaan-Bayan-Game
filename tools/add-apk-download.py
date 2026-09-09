from pathlib import Path

INDEX = Path("index.html")
APK_URL = "https://github.com/Jihoooon14/Hulaan-Bayan-Game/releases/download/android-latest/Hulaan-Bayan-Android.apk"

if not INDEX.exists():
    raise SystemExit("index.html was not found in the repository root.")

text = INDEX.read_text(encoding="utf-8")

if APK_URL in text:
    print("Android APK link already exists.")
    raise SystemExit(0)

old_hero = (
    '<a class="button secondary" href="downloads/Hulaan-Bayan-Game.zip" '
    'download>Download Python game</a>'
)
new_hero = (
    f'<a class="button secondary" href="{APK_URL}" download>'
    'Download Android APK</a>'
    '<a class="button secondary" href="downloads/Hulaan-Bayan-Game.zip" '
    'download>Download Python game</a>'
)

if old_hero in text:
    text = text.replace(old_hero, new_hero, 1)
else:
    print("Hero Python-download button pattern was not found; leaving hero unchanged.")

old_download = (
    '<a class="button" href="downloads/Hulaan-Bayan-Game.zip" download>'
    'Download Hulaan Bayan (.zip)</a>'
)
new_download = (
    f'<div class="actions"><a class="button" href="{APK_URL}" download>'
    'Download Android APK</a>'
    '<a class="button secondary" href="downloads/Hulaan-Bayan-Game.zip" download>'
    'Download Windows/Python ZIP</a></div>'
)

if old_download in text:
    text = text.replace(old_download, new_download, 1)
else:
    print("Main ZIP-download button pattern was not found; leaving that section unchanged.")

old_note = (
    'Play free on phone or computer &middot; Python desktop download also available'
)
new_note = (
    'Play online on phone or computer &middot; Android APK and Python desktop download available'
)
text = text.replace(old_note, new_note, 1)

INDEX.write_text(text, encoding="utf-8")
print("index.html updated with Android APK download link.")
