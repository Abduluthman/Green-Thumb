# Changelog

## Unreleased — repository modernization

- Rebuilt the UI around shared templates, responsive CSS and explicit upload/camera workflows.
- Reworked the visual language after a frontend audit: direct copy, system typography, flatter surfaces, fewer decorative elements and consistent task/result layouts.
- Replaced placeholder project documentation with setup instructions, a verified research citation, a model card and an engineering review.
- Protected administration with configured password hashes, expiring sessions, CSRF checks and rate limits.
- Replaced JSON feedback writes with SQLite transactions and safe text rendering.
- Added validated image inputs, lazy model loading, explicit uncertainty and deployment-independent API URLs.
- Added Python tests, frontend DOM tests, lint/format checks, dependency manifests and GitHub CI.
- Migrated the waste dictionary to a versioned schema with independent streams, risk levels, handling flags, disposal routes, jurisdictions and evidence metadata.
- Added ranked dictionary search, stream/risk filters, official-reference panels and an optional subtype step after broad model predictions.
- Added contextual dictionary-correction reports to the authenticated administrator feedback queue.
- Documented the dictionary editorial policy and preserved unverified legacy advice with an explicit historical status.
- Excluded historical feedback, model weights and local originals from the public repository.

The historical README identified the final year application as version 2.3. Its source and original images remain in the ignored local backup. This modernization is not assigned an experimental result or a new public release version.
