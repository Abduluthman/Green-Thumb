<p align="center">
  <img src="static/leaf.svg" width="72" height="72" alt="Green Thumb leaf">
</p>

# Green Thumb

[![Checks](https://github.com/Abduluthman/Green-Thumb/actions/workflows/ci.yml/badge.svg)](https://github.com/Abduluthman/Green-Thumb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-2f6246.svg)](LICENSE)

**A real-time seven-class waste classification system combining deep learning, Flask deployment, and practical disposal guidance.**

Green Thumb was developed as my final-year Computer Science project at Baze University and later formed the basis of published research on real-time waste classification in smart IoT environments.

The application classifies waste into:

**Cardboard · Glass · Metal · Organic · Paper · Plastic · Trash**

and connects predictions to a searchable disposal-guidance dictionary containing **136 waste entries**.

---

## Highlights

- Real-time image classification
- Seven waste categories
- MobileNet-style deep-learning backbone
- Flask-based web application
- Image-upload and camera workflows
- Searchable disposal-guidance dictionary
- Optional subtype refinement for more specific guidance
- Confidence-based fallback to `Not Classified`
- SQLite feedback collection
- Authenticated administrator review
- Responsive frontend using Jinja, JavaScript and CSS
- Peer-reviewed publication derived from the underlying research

---

## Research Publication

This project formed the basis of work associated with:

**E. Omonayin, O. N. Akande, A. Muhammad, and S. Enemuo (2025).**  
*Evaluating Deep Learning Models for Real-Time Waste Classification in Smart IoT Environment.*  
**Nigerian Journal of Technology, 44(2), 357–366.**

**DOI:** [10.4314/njt.v44i2.18](https://doi.org/10.4314/njt.v44i2.18)

The published work compares MobileNet, InceptionV3 and VGG16 approaches for waste classification in a smart IoT context.

This repository focuses primarily on the application workflow and modernized software implementation.

> **Important reproducibility note:**  
> The repository is not presented as a complete reproduction package for the published experiments. The supplied application model contains a MobileNet-style backbone and seven-class output head, but the original experiment notebooks, training pipeline and evaluation dataset are not included. Published metrics should therefore not be interpreted as independently reproduced results for the exact model file used by this repository.

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

---

## Core Features

### Image Classification

Upload an image and classify it into one of seven waste categories:

- Cardboard
- Glass
- Metal
- Organic
- Paper
- Plastic
- Trash

### Camera Classification

Start the browser camera, choose a frame and submit it for classification.

### Disposal Guidance Dictionary

Search and filter across **136 waste entries** containing practical guidance such as:

- waste stream
- preparation steps
- disposal routes
- handling considerations
- evidence status
- related official sources

### Prediction Refinement

After receiving a broad predicted class, users can optionally choose a more specific subtype to receive more targeted disposal guidance for items such as:

- broken glass
- aerosols
- food-soiled packaging
- other ambiguous waste items

### Confidence Handling

Predictions below the configured classification threshold return:

```text
Not Classified
```

rather than forcing a low-confidence class.

### Feedback Collection

User feedback is stored in SQLite and can be reviewed through an authenticated administrator dashboard.

---

## Technology Stack

### Backend

- Python
- Flask
- SQLite

### Machine Learning

- TensorFlow
- Keras
- NumPy
- Pillow

### Frontend

- Jinja templates
- JavaScript
- Responsive CSS

### Testing and Quality

- Pytest
- Ruff
- JavaScript syntax checks
- Automated CI on Linux and Windows

No frontend build step is required to run the application.

---

## Quick Start

Use **Python 3.11 or 3.12**.

Run all commands from the repository root.

```bash
git clone https://github.com/Abduluthman/Green-Thumb.git
cd Green-Thumb
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Dictionary browsing and feedback submission work immediately after installing the base dependencies.

Administrator login is disabled until credentials are configured.

Without the optional ML dependencies and model weights, image classification returns an explicit unavailable message while the rest of the application remains usable.

---

## Enable Image Classification

Install the optional machine-learning dependencies:

```bash
python -m pip install -r requirements-ml.txt
```

On Windows, if the virtual environment is not activated:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
```

Place a trusted `model.h5` file at the repository root, or set the `MODEL_PATH` environment variable to the model's absolute path.

Restart the application after configuring the model.

The model is loaded lazily on the first classification request.

The historical local model artifact is approximately:

```text
143,028,840 bytes
```

and is intentionally excluded from Git.

A public model download is not currently distributed through this repository.

See the [Model Card](docs/MODEL_CARD.md) for additional information about:

- model provenance
- checksum information
- architecture assumptions
- known limitations
- reproducibility constraints

---

## Supported Image Inputs

Use one clearly visible object per image.

Supported formats:

- JPEG
- PNG
- WebP

Application limits include:

- maximum request size: 8 MiB
- maximum image size: 16 megapixels

Camera access generally requires:

- `localhost`, or
- HTTPS

Images are processed in memory and are not intentionally persisted by the application.

---

## Inference Pipeline

```text
Image upload / selected camera frame
    ↓
Format, byte and pixel validation
    ↓
RGB conversion
    ↓
Resize to 128 × 128
    ↓
Normalize pixel values by 255
    ↓
Lazy-loaded Keras model
    ↓
Seven class scores
    ↓
Highest score > 0.7?
    ├── Yes → predicted waste class
    └── No  → Not Classified
    ↓
Matching disposal guidance
```

The configured class order and confidence threshold originate from the original application.

A model score should not automatically be interpreted as a calibrated probability of correctness.

Predictions and disposal guidance should be checked against local waste-management rules, particularly for:

- hazardous materials
- unfamiliar materials
- locally regulated waste streams

---

## Model Validation Utility

Use:

```bash
python scripts/check_model.py
```

to verify that the configured model:

- loads successfully
- accepts an input
- executes inference
- returns output in the expected structural format

You can also pass a real image path.

This utility validates execution compatibility only.

It does **not** independently validate:

- model accuracy
- class mapping correctness
- calibration
- generalization performance

---

## Configure Administrator Access

Generate a random session key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Generate a password hash:

```bash
python -c "from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass('Admin password: ')))"
```

Set the resulting values as environment variables.

### Windows PowerShell

```powershell
$env:SECRET_KEY = 'paste-generated-session-key'
$env:ADMIN_PASSWORD_HASH = 'paste-generated-password-hash'
.\.venv\Scripts\python.exe app.py
```

### macOS / Linux

```bash
export SECRET_KEY='paste-generated-session-key'
export ADMIN_PASSWORD_HASH='paste-generated-password-hash'
python app.py
```

`ADMIN_USERNAME` defaults to:

```text
admin
```

Never commit real credentials.

The repository includes:

```text
.env.example
```

as a configuration reference.

It is **not automatically loaded** by the application.

---

## Repository Structure

```text
app.py
    Flask application factory, routes, sessions and feedback storage

classifier.py
    Image validation, preprocessing and model inference

dictionary.json
    Versioned catalogue containing 136 disposal-guidance entries

templates/
    Shared Jinja layouts and feature pages

static/
    CSS, JavaScript and project artwork

tests/
    Request, security, storage and inference-contract tests

scripts/
    Model and utility scripts

docs/
    Model card, validation notes, engineering review,
    deployment documentation and publishing guidance

.github/workflows/
    Automated CI checks for supported platforms
```

Runtime application data is stored inside the ignored:

```text
instance/
```

directory.

Historical local artifacts such as:

- `feedback.json`
- model weights
- `.local-backup/`

are intentionally excluded from a clean repository clone.

The local backup preserves material from the pre-modernization version of the application.

---

## Development and Validation

Install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the Python test suite:

```bash
python -m pytest -q
```

Run linting:

```bash
python -m ruff check .
```

Check JavaScript syntax:

```bash
node --check static/app.js
```

Install frontend test dependencies:

```bash
npm ci
```

Run frontend tests:

```bash
npm test
```

Node.js **22.14+** is required only for frontend development checks.

It is not required to run the Flask application.

Automated tests cover areas including:

- request handling
- authentication and security behavior
- feedback storage
- model-inference contracts
- ranked dictionary search
- filters
- evidence rendering
- classification refinement
- feedback escaping

CI runs supported Python versions on Linux and Windows without downloading model weights.

These checks validate application behavior and engineering contracts.

They do **not** independently validate:

- classification accuracy
- disposal-guidance correctness
- model calibration
- real-device camera compatibility

See [docs/VALIDATION.md](docs/VALIDATION.md) for the current validation record.

---

## Documentation

Additional project documentation is available here:

- [Dictionary Guide](docs/DICTIONARY.md)
- [Model Card](docs/MODEL_CARD.md)
- [Validation Record](docs/VALIDATION.md)
- [Frontend / UI-UX Audit](docs/UI_UX_AUDIT.md)
- [Engineering Review](docs/REVIEW.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [GitHub Publishing Guide](docs/GITHUB_RELEASE.md)

---

## Repository Status

**Maintained research prototype**

This repository contains a modernized application based on the original final-year project.

The current repository should not be interpreted as:

- a complete reproduction package for the journal publication
- a fully validated commercial waste-identification product
- authoritative waste-management guidance for every jurisdiction

Dictionary functionality can be used without ML model weights.

Image classification requires a separately supplied compatible model.

---

## Roadmap

Planned improvements include:

- Recover the original training pipeline
- Recover and verify the original class-index mapping
- Evaluate the exact distributed model against a held-out dataset
- Publish reproducible evaluation results
- Complete per-entry disposal-guidance review
- Add stronger provenance information for disposal guidance
- Perform real-browser and mobile-device testing
- Perform additional camera testing
- Conduct structured user testing
- Improve model calibration and uncertainty handling
- Publish a reproducible model artifact where licensing and provenance permit
- Explore deployment of the complete application

The [Engineering Review](docs/REVIEW.md) contains additional findings and prioritized recommendations.

---

## License and Attribution

Application source code is available under the [MIT License](LICENSE), preserving the licensing choice of the original project.

The associated journal article is governed by its publisher's terms.

The software license does not automatically establish rights to:

- separately distributed model weights
- external datasets
- third-party images
- third-party documentation
- external research material

Any separately distributed model or dataset should therefore include its own provenance, licensing and attribution information.

---

## Citation

If referencing the associated research, cite:

> E. Omonayin, O. N. Akande, A. Muhammad, and S. Enemuo.  
> “Evaluating Deep Learning Models for Real-Time Waste Classification in Smart IoT Environment.”  
> *Nigerian Journal of Technology*, vol. 44, no. 2, pp. 357–366, 2025.  
> https://doi.org/10.4314/njt.v44i2.18

Machine-readable citation metadata is available in:

```text
CITATION.cff
```

---

## Author

**Abdulwahab Uthman Muhammad**

- GitHub: [@Abduluthman](https://github.com/Abduluthman)
- LinkedIn: [Abdulwahab Muhammad](https://www.linkedin.com/in/abdulwahab-muhammad)

---

## Disclaimer

Green Thumb is a research and portfolio project.

Classification predictions may be incorrect, and disposal requirements vary by location.

Always verify disposal instructions against relevant local waste-management guidance, particularly for hazardous or regulated materials.
