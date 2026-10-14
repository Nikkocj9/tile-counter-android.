# Tile Counter Android project

This project is an Android-oriented Kivy rewrite of the supplied Tkinter Tile Counter.

## Important notes
- This is a converted app project, not an APK yet.
- The original Tkinter interface cannot be packaged unchanged as a normal Android app with Buildozer; this version uses Kivy.
- Counting, tile selection, undo, reset, saved entries, totals, JSON persistence and CSV generation are included.
- The CSV is currently written into Kivy's app-private data directory. On Android, that location is not normally visible in the public Downloads folder. A future enhancement can add Android's Save As / share sheet using the Storage Access Framework.
- Test on the phone before relying on it for warehouse records. Keep backups of any existing data from the original Pydroid/Tkinter app; the new app uses a separate storage location and does not automatically import old records.

## Build APK using only your phone
The build happens on GitHub's hosted Linux runner, so the phone does not need to compile Android SDK/NDK locally.

1. Sign in to GitHub in your phone browser and create a new repository, for example `tile-counter-android`.
2. Upload the files from this project to the repository, preserving the `.github/workflows/build-apk.yml` path.
3. Open the repository's **Actions** tab.
4. Choose **Build Tile Counter APK** and tap **Run workflow** (or push to the `main` branch).
5. Wait for the workflow to finish successfully.
6. Open the completed workflow run, find **Artifacts**, and download `tile-counter-debug-apk`.
7. Extract the ZIP artifact on your phone, tap the `.apk`, and allow installation from that source if Android asks.

GitHub may ask you to verify your account or enable Actions. The exact screen labels can vary.

## Files
- `main.py`: Kivy app.
- `buildozer.spec`: Android packaging configuration.
- `.github/workflows/build-apk.yml`: cloud build workflow.

## Data
The app writes `state.json`, `records.json`, and `tile_records.csv` under the app's private data directory. Uninstalling the app may delete this data, so export/backup records before uninstalling.
