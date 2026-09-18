# GitHub publishing guide

## Suggested repository presentation

- **Name:** `green-thumb`
- **Description:** Research-backed waste classification and disposal guidance with Flask and TensorFlow. Baze University final year project connected to a NIJOTECH publication.
- **Topics:** `waste-classification`, `machine-learning`, `tensorflow`, `flask`, `mobilenet`, `sustainability`, `computer-vision`, `final-year-project`
- **Website:** use the publication DOI until a tested demo is deployed.

The directory has been initialized as its own Git repository. No remote or commit is created by this preparation. Review changes and add the intended project files from this directory, rather than from the enclosing home-directory repository.

```bash
git status --short
git add .
git diff --cached --stat
git diff --cached --check
git status --short
```

Check the staged list: it should include source, documentation and tests, and exclude `.env`, `.venv`, `.local-backup`, `instance`, historical `feedback.json` and all model weights. Then:

```bash
git commit -m "Prepare Green Thumb research application for public release"
```

Create an empty GitHub repository under your chosen account, copy its remote URL, then:

```bash
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

These are publishing instructions, not actions already performed. The GitHub CLI is another option if you use it, but no account connection is required for local preparation.

## Release assets

The original model is approximately 136.4 MiB and should not be added as an ordinary Git blob. Keep it separate, or set up Git LFS intentionally. GitHub documents its [large-file limits and alternatives](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Before uploading model weights, document their provenance and redistribution permission. A release asset should include the checksum from the [model card](MODEL_CARD.md). Add the actual download URL to the README only after that release exists. The code remains runnable in dictionary mode without it.

## Final presentation pass

Open the local app at desktop and phone widths, verify camera access on a real device, and capture actual screenshots for the README. Confirm that all links work after publishing and that the CI matrix passes on GitHub. Add a short demo recording when available. Do not label this a production service or claim that CI reproduces the paper's experiments.

The source code keeps the original README's MIT licensing choice. The publication has separate terms. Historical photos/icons are preserved locally in `.local-backup/images/` and kept out of the public source set until their attribution is established; the current UI uses a repository-authored SVG illustration.
