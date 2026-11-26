# Install AI PINTAR 2.0 staging on GitHub from Android

The workflow is manual-only and runs **only** on `ai-pintar-2-staging`. It does not alter the `main` branch, AI PINTAR 1 workflow, or its schedule.

## A. Upload the package ZIP

1. Open the repository `ai-pintar-auto-video` and switch to branch `ai-pintar-2-staging`.
2. Use **+ → Upload files**.
3. Upload the file named `aipintar2_staging_package.zip` to the repository root.
4. Commit the upload to `ai-pintar-2-staging`.

## B. Create the workflow file

1. Still on `ai-pintar-2-staging`, use **+ → Create new file**.
2. File name: `.github/workflows/ai-pintar-2-staging.yml`.
3. Copy the complete YAML from `docs/INSTALL_WORKFLOW.yml` in the package into the editor.
4. Commit to `ai-pintar-2-staging`.

## C. Run the safe offline check

1. Open **Actions**.
2. Select **AI PINTAR 2.0 STAGING**.
3. Press **Run workflow**, branch `ai-pintar-2-staging`.
4. Leave both inputs `live_media=false` and `cloudinary_test=false`.
5. Run it. The job extracts the ZIP, installs dependencies, runs tests, creates a synthetic 30-second render, checks QC and stores an artifact.
6. Inspect the artifact video and logs before doing anything else.

## D. Optional live media test

Only after the offline run succeeds, add `PIXABAY_API_KEY` under repository **Settings → Secrets and variables → Actions → New repository secret**. Do not paste it in a file or chat.

Run the workflow with `live_media=true`, `cloudinary_test=false`. This fetches real footage and uses Edge TTS, but **does not publish**.

## E. Optional Cloudinary upload test

After a live-media run succeeds, add Cloudinary secrets (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`). Run with `live_media=true` and `cloudinary_test=true`. It uploads to the staging folder. Buffer is not called.

## F. Rollback

Delete/revert the staging branch or its package/workflow files. Do not change `main`; no production workflow or schedule has been edited. Do not merge this branch without approval.
