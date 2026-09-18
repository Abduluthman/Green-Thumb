# Validation record

Preparation date: **18 September 2026**.

## Environment

- Windows, Python 3.12, Node.js 22.14.
- Flask 3.1.3, Flask-WTF 1.3.0, Flask-Limiter 4.1.1, NumPy 2.5.3, Pillow 12.3.0 and pytest 9.1.1.
- Frontend development dependencies are recorded in `package-lock.json`.

## Checks

| Check | Result / scope |
| --- | --- |
| `python -m pytest -q` | 63 tests passed; public routes, protected admin access, login/logout, CSRF, input validation, upload limits, feedback concurrency, model unavailability, inference contract and dictionary schema/source validation |
| `npm test` | Eleven DOM tests passed; ranked dictionary search, stream/risk filters, detail evidence, classification refinement, contextual correction reports, literal feedback rendering, network errors and camera inactivity at page load |
| `python -m ruff check .` | Passed |
| `node --check static/app.js` | Passed |
| `npm ci` and `npm run check` | Clean lockfile install succeeded; JavaScript syntax and frontend formatting passed |
| Documentation and asset links | Local Markdown links, rendered page navigation and static asset routes passed |
| Model file inspection | HDF5 metadata, input shape, seven-class softmax head, file size and SHA-256 inspected |
| Dictionary inspection | Schema version 2; 136 unique entries; controlled streams, risks and routes; valid source references; all seven classifier labels present |
| Local HTTP liveness | `GET /health` returned 200 and `{"status":"ok"}` |
| Git exclusions | Confirmed model, private feedback, local backup, database, virtual environment and Node dependencies are ignored |

The CI workflow is prepared for Linux and Windows on Python 3.11/3.12. It has not yet run on GitHub because no remote has been published.

## What was not verified

**Real TensorFlow inference:** installation of TensorFlow 2.20 first hit Windows' path-length limit in this deeply nested workspace. A retry using extended-length paths then failed for insufficient disk space. The partial TensorFlow package was removed. The original `model.h5` was not changed. The base application and contract tests run, but a real prediction cannot be claimed from this session.

To finish: create the ML environment at a shorter path with sufficient free disk space, install `requirements-ml.txt`, then run `python scripts/check_model.py` and test known images. The base requirements are sufficient for dictionary-only use.

**Visual and device validation:** no connected browser was available, including the in-app browser. DOM tests do not measure layout, screen-reader behavior, file-picker behavior, camera permissions or real camera capture. Review the app at desktop and phone widths and verify these flows before recording screenshots or promoting a hosted demo.

**Model quality and research reproducibility:** no labelled benchmark, class-index artifact or experiment notebook was available. The tests do not establish accuracy, safety of disposal guidance, inference latency or reproduction of the publication's results.
