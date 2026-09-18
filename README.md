<p align="center"><img src="static/leaf.svg" width="64" height="64" alt="Green Thumb leaf"></p>

# Green Thumb

[![Checks](https://github.com/Abduluthman/Green-Thumb/actions/workflows/ci.yml/badge.svg)](https://github.com/Abduluthman/Green-Thumb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-2f6246.svg)](LICENSE)

**Practical waste classification and disposal guidance.**

A waste-classification and disposal-guidance application built as a Baze University final year project by **Abdulwahab Uthman Muhammad**. Green Thumb connects image-based classification with a searchable dictionary so that identifying an item leads to a practical next step.

[Read the publication](https://doi.org/10.4314/njt.v44i2.18) · [Dictionary guide](docs/DICTIONARY.md) · [Model card](docs/MODEL_CARD.md) · [Frontend audit](docs/UI_UX_AUDIT.md) · [Engineering review](docs/REVIEW.md) · [Deployment](docs/DEPLOYMENT.md)

**Status:** maintained research prototype. The repository contains a modernized application, not a complete reproduction package for the publication. Dictionary browsing works without model weights; image classification requires a separately supplied model.

## What it does

- **Identify an image:** classify a photo into Cardboard, Glass, Metal, Organic, Paper, Plastic or Trash.
- **Scan with a camera:** start the camera and choose when to send a frame for classification.
- **Explore 136 dictionary entries:** search and filter by waste stream or handling risk, then review preparation, disposal routes, evidence status and related official sources.
- **Refine broad predictions:** choose an optional subtype after classification to find more specific guidance for items such as broken glass, aerosols or food-soiled packaging.
- **Handle uncertainty:** predictions below the original confidence threshold return “Not Classified”.
- **Collect feedback:** store submissions in SQLite for review through an authenticated administrator dashboard.

The frontend uses shared Jinja templates, plain JavaScript and responsive CSS. Flask handles requests, Pillow/NumPy prepare images, and TensorFlow/Keras runs inference. No frontend build step is required.

## Research context

This final year application formed the basis of work associated with:

**E. Omonayin, O. N. Akande, A. Muhammad, and S. Enemuo (2025).** *Evaluating Deep Learning Models for Real-Time Waste Classification in Smart IoT Environment.* Nigerian Journal of Technology, **44**(2), 357–366. [doi:10.4314/njt.v44i2.18](https://doi.org/10.4314/njt.v44i2.18).

The paper compares MobileNet, InceptionV3 and VGG16. This repository focuses on the application workflow. Its supplied model contains a MobileNet-style backbone and a seven-class head; the original experiment notebooks and evaluation dataset are not present. The paper's results are not presented as independently reproduced metrics for this exact model file. See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## Quick start

Use **Python 3.11 or 3.12**. Run all commands from the repository root.

```bash
git clone https://github.com/Abduluthman/Green-Thumb.git
cd Green-Thumb
```

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**. You can immediately browse the dictionary and submit feedback. Administrator login is disabled until configured. Without the ML dependencies and weights, classification returns an explicit unavailable message while other features remain usable.

### Enable image classification

Install the optional ML dependencies in the same environment:

```bash
python -m pip install -r requirements-ml.txt
```

On Windows without activating the environment, use `.\.venv\Scripts\python.exe` instead of `python`.

Place a trusted `model.h5` at the repository root, or set `MODEL_PATH` to its absolute path, then restart the app. The model is loaded on the first classification request. The local historical model is **143,028,840 bytes** and is excluded from Git. A public download has not yet been published; obtain the artifact from the maintainer. See the [model card](docs/MODEL_CARD.md) for its checksum and provenance limitations.

Use one clearly visible object per image. Supported formats: JPEG, PNG and WebP, up to an 8 MiB request and 16 megapixels. Camera access works on localhost or HTTPS. Images are processed in memory and are not saved by this application.

Run `python scripts/check_model.py` to check that the weights load and accept a synthetic image, or pass a real image path. This checks execution only, not accuracy.

### Configure administrator access

Generate a random session key and a password hash with your environment's Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass('Admin password: ')))"
```

Set `SECRET_KEY` and `ADMIN_PASSWORD_HASH` to those generated values before starting the app. `ADMIN_USERNAME` defaults to `admin`. In PowerShell use single quotes so the password hash's dollar signs remain literal:

```powershell
$env:SECRET_KEY = 'paste-generated-session-key'
$env:ADMIN_PASSWORD_HASH = 'paste-generated-password-hash'
.\.venv\Scripts\python.exe app.py
```

On macOS/Linux use `export SECRET_KEY='…'` and `export ADMIN_PASSWORD_HASH='…'`. Never commit real values. `.env.example` documents the settings; it is **not automatically loaded**.

## How it works

```text
Image upload / chosen camera frame
    → format, byte and pixel validation
    → RGB · 128 × 128 · pixel values / 255
    → lazy-loaded Keras model
    → seven class scores
    → highest score > 0.7? predicted class : Not Classified
    → matching dictionary guidance
```

The threshold and class order come from the original application. A model score is not a calibrated probability of correctness. Predictions and dictionary entries should be checked against local waste-collection rules, especially for hazardous or unfamiliar materials.

## Repository map

```text
app.py                  Flask factory, routes, sessions and feedback storage
classifier.py           Image validation, preprocessing and model inference
dictionary.json         Versioned catalogue with 136 disposal-guidance entries
templates/              Shared layout and feature pages
static/                 CSS, JavaScript and leaf artwork
tests/                  Request, security, storage and inference-contract tests
docs/                   Model card, review, deployment and publishing notes
.github/workflows/      Automated checks on Linux and Windows
```

Runtime data lives in ignored `instance/`. Historical `feedback.json`, the model, and `.local-backup/` are retained only in the original local workspace; they are not part of a clean clone. The backup preserves the pre-modernization app/pages and original imagery.

## Development and validation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
node --check static/app.js
npm ci
npm test
```

Node.js 22.14+ is needed only for frontend development checks, not to run the app. DOM tests cover ranked dictionary search, filters, evidence rendering, classification refinement and feedback escaping; they do not replace a real browser/device test. CI exercises Python 3.11/3.12 on Linux and Windows without downloading model weights. These tests validate application behavior, not classification accuracy or disposal advice. The [validation record](docs/VALIDATION.md) states what has been checked locally and what remains unverified.

## What comes next

The most valuable next work is recovering the training pipeline and class-index mapping, evaluating the exact model on a held-out dataset, completing the per-entry FCT disposal review, and testing the app with real users and camera devices. The [engineering review](docs/REVIEW.md) explains the original findings, fixes and prioritized roadmap.

For hosting, follow the [deployment notes](docs/DEPLOYMENT.md). For repository presentation and the first push, use the [GitHub publishing guide](docs/GITHUB_RELEASE.md).

## License and attribution

Application source is available under the [MIT License](LICENSE), preserving the original project's licensing choice. The linked journal article is governed by its own publisher terms. Model weights and any separately distributed dataset or third-party assets require their own provenance and permissions; the software license does not establish those rights.
