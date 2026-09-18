"""Lazy model loading keeps dictionary-only installations lightweight."""

from pathlib import Path
from threading import Lock
import warnings

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

LABELS = ("Cardboard", "Glass", "Metal", "Organic", "Paper", "Plastic", "Trash")
THRESHOLD = 0.7  # Original application threshold; not a calibrated probability.
MAX_PIXELS = 16_000_000


class InvalidImage(ValueError):
    pass


class ModelUnavailable(RuntimeError):
    pass


def preprocess_image(stream):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(stream) as image:
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise InvalidImage("Use a JPEG, PNG or WebP image.")
                if image.width * image.height > MAX_PIXELS:
                    raise InvalidImage("Image exceeds the 16 megapixel limit.")
                image = ImageOps.exif_transpose(image).convert("RGB").resize((128, 128))
                return np.asarray(image, dtype=np.float32)[None, ...] / 255.0
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise InvalidImage("The image could not be read. Try another JPEG, PNG or WebP file.") from error


class Classifier:
    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self._model = None
        self._lock = Lock()

    def classify(self, stream):
        image = preprocess_image(stream)
        with self._lock:
            try:
                if self._model is None:
                    if not self.model_path.is_file():
                        raise FileNotFoundError(self.model_path)
                    from tensorflow.keras.models import load_model

                    self._model = load_model(self.model_path, compile=False)
                prediction = np.asarray(self._model.predict(image, verbose=0))
                if (
                    prediction.shape != (1, len(LABELS))
                    or not np.isfinite(prediction).all()
                    or np.any(prediction < 0)
                    or np.any(prediction > 1)
                    or not np.isclose(prediction.sum(), 1, atol=0.01)
                ):
                    raise ValueError("Expected seven finite softmax class scores.")
            except Exception as error:
                raise ModelUnavailable("Model loading or prediction failed.") from error
        confidence = float(prediction.max())
        return {
            "class": LABELS[int(prediction.argmax())] if confidence > THRESHOLD else "Not Classified",
            "confidence": round(confidence, 4),
        }
