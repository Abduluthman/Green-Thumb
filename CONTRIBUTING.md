# Contributing

Green Thumb is a research application with a deliberately small Flask codebase. Start by reading the README, model card and engineering review.

Use Python 3.11 or 3.12 and a virtual environment:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
node --check static/app.js
npm ci
npm test
npm run check
```

Base tests do not require TensorFlow or real weights. They exercise request handling, access control, feedback persistence and the inference contract with test models. When changing inference, also run a real-model smoke check and compare preprocessing and label order against training records.

Keep changes focused. Explain the user-visible problem, change and validation in your pull request. Dictionary corrections should include a reliable source and the location to which the advice applies. Never commit private feedback, credentials, datasets or weights without appropriate permission.

Before changing a page, check keyboard access, phone-width layout, loading/error states and camera cleanup where applicable. Keep user-provided text out of `innerHTML`. Changing the seven-class mapping or normalization requires evidence from the training pipeline.
