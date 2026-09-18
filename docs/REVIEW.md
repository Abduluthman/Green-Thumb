# Engineering review and product roadmap

## Assessment

The strongest portfolio story is the connection between an end-user waste-classification application and published comparative deep-learning research. The original code demonstrated that workflow, but its repository packaging, access control and runtime assumptions made it difficult to share as a maintainable application.

The modernization preserves the seven classes, dictionary content, original model bytes and principal application routes. It changes the UI and operational behavior, so this version should be described as a maintained successor to the final year implementation, not the exact experimental artifact used for the paper.

## Findings addressed

| Original finding | Why it mattered | Change |
| --- | --- | --- |
| Hardcoded `admin` / `password`, no session authentication | Anyone could bypass login and read feedback | Environment-configured password hash, expiring session, protected pages/API, logout and login throttling |
| Feedback inserted through `innerHTML` | Stored markup could execute in an administrator's browser | Feedback now renders with DOM `textContent`; a restrictive content security policy provides an additional boundary |
| Unrestricted template route | Root files and internal templates could be exposed or cause confusing errors | Explicit page allowlist and a dedicated JSON dictionary endpoint |
| Global permissive CORS and localhost API URLs | Poor deployment portability and unnecessary cross-origin access | Same-origin API URLs, CSRF protection and no permissive CORS |
| No image size/format/mode handling | Invalid, grayscale or large images could crash or exhaust the process | Byte/pixel limits, RGB conversion, decode validation and structured errors |
| Model loaded at import time | All features failed if TensorFlow or weights were unavailable | Lazy loading; dictionary and feedback work without inference dependencies |
| JSON read-modify-write feedback store | Concurrent writes could lose submissions | Parameterized SQLite transactions and UTC timestamps |
| Camera sent a frame every second regardless of inference time | Overlapping requests, unnecessary capture and poor failure behavior | User-triggered scanning, one in-flight request, camera shutdown on navigation/backgrounding |
| Missing CSS files, repeated page styling and fixed widths | Broken asset requests, inconsistent layout and mobile overflow | Shared templates, stylesheet and script with responsive layout and keyboard-accessible controls |
| Manually duplicated dictionary index and mixed category meanings | Entries could disagree with the JSON source, and material, risk and route were conflated | Versioned 136-entry catalogue with ranked search, filters, separate streams/risks/routes and validated source references |
| Placeholder README, no tests or dependency files | Difficult for reviewers to understand or run | Project overview, research citation, setup, model card, tests and CI |
| Private feedback and oversized model beside source | Accidental data publication and failed normal Git pushes | Ignore rules; local originals preserved outside the publication set |

## Highest-value next steps

### 1. Recover reproducibility evidence

Bring back the training notebooks, exact dataset reference/version, permitted access instructions, train/validation/test split manifest, seeds, augmentation settings and class-index mapping. Evaluate this exact checksum on the held-out set. Publish per-class precision/recall/F1, a confusion matrix and failure examples. Separate training time from inference latency. These artifacts would strengthen the research story more than another UI feature.

### 2. Validate usefulness with real users

Test clear single-object images, mixed materials, poor lighting and unfamiliar objects. Record how often users receive a correct and locally actionable recommendation, not just the top-1 label. Compare user-triggered camera scans with optional paced continuous scanning only after measuring inference latency. Add stronger uncertainty guidance if the model is confidently wrong.

### 3. Complete the local dictionary review

The application now records source, date, jurisdiction and evidence status, and links relevant records to official AEPB/FCTA, NESREA, NAFDAC and WHO material. The original wording is deliberately labelled historical unless it has related evidence. The remaining work is a line-by-line review with a suitable FCT waste-management source, followed by a verified directory of collection services and accepted materials. See the [dictionary editorial guide](DICTIONARY.md).

### 4. Prepare an operated service

Choose a deployment target and expected traffic. Add HTTPS, trusted proxy configuration, shared rate-limit storage if scaling, logs/metrics, database backup and restore checks, retention/deletion tooling and abuse monitoring. Load-test inference and establish timeouts and resource limits. See [deployment notes](DEPLOYMENT.md).

### 5. Improve maintainability as scope grows

Split routes into blueprints when a second developer or feature set warrants it. Add browser regression tests, accessibility checks, screenshots and camera-device tests. Introduce a migration tool when the schema changes. A framework rewrite or microservices are not prerequisites for demonstrating sound engineering here.

## Remaining limitations of this preparation

- No browser automation connection was available for visual or real-camera verification; responsive styling has not been visually signed off.
- No benchmark dataset or experiment records were supplied, so model accuracy and the publication's results were not reproduced.
- Historical `feedback.json` remains private and is not automatically imported into the new database.
- A public model download and the GitHub remote have not been created.
- Dependency ranges are compatibility constraints, not a full reproducible lockfile. Record a tested deployment environment before operating a hosted service.

See [validation record](VALIDATION.md) for the checks actually run.

The later [frontend and UI/UX audit](UI_UX_AUDIT.md) documents the move from an editorial landing-page style to a quieter task-focused interface.
