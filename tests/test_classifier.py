import io

import numpy as np
from PIL import Image
import pytest

from classifier import Classifier, InvalidImage, ModelUnavailable, preprocess_image


def image_stream(mode="RGB", size=(10, 10), format="PNG"):
    stream = io.BytesIO()
    Image.new(mode, size).save(stream, format=format)
    stream.seek(0)
    return stream


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "L", "P"])
def test_image_modes_normalized(mode):
    image = preprocess_image(image_stream(mode))
    assert image.shape == (1, 128, 128, 3)
    assert image.dtype == np.float32
    assert 0 <= image.min() <= image.max() <= 1


def test_unsupported_image_format():
    with pytest.raises(InvalidImage):
        preprocess_image(image_stream(format="GIF"))


def test_pixel_limit(monkeypatch):
    monkeypatch.setattr("classifier.MAX_PIXELS", 99)
    with pytest.raises(InvalidImage):
        preprocess_image(image_stream())


@pytest.mark.parametrize(
    "prediction, expected",
    [
        ([[0.7, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]], "Not Classified"),
        ([[0.71, 0.04, 0.05, 0.05, 0.05, 0.05, 0.05]], "Cardboard"),
    ],
)
def test_threshold(prediction, expected):
    classifier = Classifier("unused.h5")

    class Model:
        def predict(self, image, verbose=0):
            return np.array(prediction)

    classifier._model = Model()
    assert classifier.classify(image_stream())["class"] == expected


@pytest.mark.parametrize("prediction", [[[1, 0]], [[float("nan")] * 7], [[2, -1, 0, 0, 0, 0, 0]], [[0.1] * 7]])
def test_invalid_model_output(prediction):
    classifier = Classifier("unused.h5")

    class Model:
        def predict(self, image, verbose=0):
            return np.array(prediction)

    classifier._model = Model()
    with pytest.raises(ModelUnavailable):
        classifier.classify(image_stream())
