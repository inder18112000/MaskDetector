import shutil
from pathlib import Path

import numpy as np
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

from app.paths import Models

MASKED   = "mask"
UNMASKED = "no_mask"

_model = None


def _get_model() -> YOLO:
    global _model
    if _model is not None:
        return _model

    model_path = Path(Models.MASK_DETECTOR)
    if not model_path.exists():
        model_path.parent.mkdir(parents=True, exist_ok=True)
        cached = hf_hub_download(
            repo_id="Nma/Face-Mask-yolov8",
            filename="best.pt",
        )
        shutil.copy(cached, model_path)

    _model = YOLO(str(model_path))
    return _model


def detect(rgb_frame: np.ndarray):
    """
    Detect faces and classify each as masked or unmasked.

    Parameters
    ----------
    rgb_frame : np.ndarray  (H x W x 3, RGB)

    Returns
    -------
    detections : list of (x, y, w, h, status)
    has_face   : bool
    """
    model   = _get_model()
    results = model(rgb_frame, verbose=False, conf=0.45)

    detections = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            # class 0 = face (no mask), class 1 = face_masked
            status = MASKED if cls == 1 else UNMASKED
            detections.append((x1, y1, x2 - x1, y2 - y1, status))

    return detections, len(detections) > 0
