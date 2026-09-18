# Model card

## Purpose

Green Thumb predicts one of seven material categories from a single image to support an educational waste-disposal workflow. It is a research prototype, not a validated waste-sorting or hazardous-material identification system.

## Artifact inspected

| Property | Value |
| --- | --- |
| Local filename | `model.h5` (excluded from Git) |
| Size | 143,028,840 bytes (approximately 136.4 MiB) |
| SHA-256 | `7ae0ac8ae1630d7bd7b57e36736ee43e45460313a9fb317acf447a9ede05d979` |
| Saved with | Keras 3.3.3, according to HDF5 metadata |
| Architecture evidence | MobileNet-style named depthwise/pointwise convolution blocks, followed by Flatten, Dense(640), Dropout, Dense(512), Dropout, Dense(7, softmax) |
| Input | `(batch, 128, 128, 3)` RGB |
| Output order used by original application | Cardboard, Glass, Metal, Organic, Paper, Plastic, Trash |
| Decision rule | Return the highest-scoring class only when its score is strictly greater than 0.7; otherwise `Not Classified` |

The architecture description comes from inspecting the saved file. The correspondence between output indices and training labels comes from the original application code; it has not been verified against a saved training class-index file.

## Preprocessing

The application converts decoded images to RGB, corrects EXIF orientation, resizes to 128 × 128, converts to float32 and divides pixel values by 255. This preserves the original application's resizing and normalization convention, with added format handling. The training preprocessing is not included here, so this convention still needs comparison with the original training pipeline. Do not substitute a framework's default MobileNet preprocessing without checking that pipeline.

Accepted formats are JPEG, PNG and WebP, with an 8 MiB request limit and 16 million decoded pixels. Uploaded images and camera frames are processed in memory, not stored by the application.

## Research relationship and evidence limits

The related [NIJOTECH article](https://doi.org/10.4314/njt.v44i2.18) compares MobileNet, InceptionV3 and VGG16. This repository contains the application and a locally supplied model artifact; it does not contain the experiment notebooks, dataset splits or evaluation outputs needed to reproduce that comparison.

The publication's reported metrics must not be presented as independently verified performance for this exact file. No held-out accuracy, per-class precision/recall, calibration, robustness or real-time latency claim is made for this release. A successful inference smoke check demonstrates execution, not accuracy.

## Known limitations

- A single-label classifier cannot reliably describe multiple objects, mixed materials or an unfamiliar object.
- The 0.7 threshold is inherited, not calibrated. High confidence can still accompany a wrong prediction.
- Lighting, background, camera quality and local waste patterns may differ from the training data.
- “Trash” is a model label, not a local disposal instruction.
- Dataset version, split membership, seed, augmentation, class balance and checkpoint selection are not available in this directory.
- Dictionary recommendations require review against local collection rules and material-safety guidance.

## Distribution

The model stays local and is ignored by Git. To enable inference, obtain a trusted copy from the project maintainer, place it at the repository root or set `MODEL_PATH`, and install `requirements-ml.txt`.

No public model download has been published by this preparation work. Before creating a release asset, establish the dataset/weight redistribution terms and attach the checksum, training class mapping and provenance. Load only trusted model files.

Verify a received artifact:

```powershell
Get-FileHash .\model.h5 -Algorithm SHA256
```

```bash
sha256sum model.h5
```
