"""Run an inference smoke check, not an accuracy evaluation.

Usage: python scripts/check_model.py [path/to/image.jpg] [--model model.h5]
Without an image, a synthetic grey image checks the model's input/output contract.
"""

import argparse
import io
import json
from pathlib import Path
import sys
import time

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from classifier import Classifier  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path)
    parser.add_argument("--model", type=Path, default=Path(__file__).resolve().parents[1] / "model.h5")
    args = parser.parse_args()
    image_bytes = io.BytesIO()
    if args.image:
        image_bytes.write(args.image.read_bytes())
    else:
        Image.new("RGB", (128, 128), (128, 128, 128)).save(image_bytes, format="PNG")
    image_bytes.seek(0)
    classifier = Classifier(args.model)
    start = time.perf_counter()
    result = classifier.classify(image_bytes)
    print(
        json.dumps(
            {
                "input": str(args.image) if args.image else "synthetic grey image (no ground truth)",
                "result": result,
                "load_and_inference_seconds": round(time.perf_counter() - start, 3),
                "parameters": classifier._model.count_params(),
                "note": "Execution smoke check only; this does not measure accuracy or steady-state latency.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
