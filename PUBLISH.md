# Publish the browser game

Target repository: https://github.com/ashleyglitzjaranilla/Hulaan-Bayan-Game

Play address: https://ashleyglitzjaranilla.github.io/Hulaan-Bayan-Game/play.html

The browser game runs as static HTML, CSS, and JavaScript. No server, build service, or Python installation is needed to play it.

## Upload through GitHub

1. Sign in to GitHub with an account that can write to the target repository.
2. Extract `downloads/Hulaan-Bayan-Website.zip` on your computer.
3. In the repository, choose **Add file → Upload files**. Upload the extracted contents into the repository root, keeping the `assets` and `downloads` folders. Do not upload just the ZIP or put everything inside an extra enclosing folder.
4. Commit to the branch used by GitHub Pages (the existing project uses `main`). Retain the existing Pages configuration.
5. Wait for the Pages deployment to finish, then open the play address on a phone and start a round.
6. Scan the QR from the updated poster and verify that it opens `play.html`. The previous printed QR opens the project homepage; the updated homepage also includes a **Play now** button.

The website archive includes the updated QR SVG, printable PDF/PNG, and the Python game ZIP. Replace these together so printed materials and the website agree.

## Publish through this workspace

The workspace Git remote points to `Jihoooon14/Hulaan-Bayan-Game`, a different repository. An isolated checkout of the intended repository was prepared at `.previews/publish-browser`.

The current GitHub credentials identify `Jihoooon14`. A publication permission check against the target repository returned HTTP 403. Sign in with an authorized account, or grant `Jihoooon14` collaborator access and accept the invitation, before pushing to the intended repository. No changes have been pushed to either repository.

The latest edits and the browser game are available locally regardless of publishing access. Open `play.html` for a local preview.
