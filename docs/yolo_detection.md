# YOLO-Based Mask Detection

## Overview

The mask detection pipeline replaces the previous Haar cascade approach with a YOLOv8 model.
Detection and person tracking are split across two files:

| File | Responsibility |
|---|---|
| `app/camera/mask_detector.py` | Load YOLO model, run inference on each frame |
| `app/camera/tracker.py` | Assign stable IDs to faces, count unique persons |

---

## 1. Model — `mask_detector.py`

### Model source

The model is downloaded automatically on first run from Hugging Face:

```
repo: Nma/Face-Mask-yolov8
file: best.pt
saved to: assets/models/face_mask.pt
```

It is cached locally after the first download; subsequent runs load directly from disk.

### Classes

| Class ID | Label | Meaning |
|---|---|---|
| 0 | `no_mask` | Face detected, no mask worn |
| 1 | `face_masked` | Face detected, mask worn |

### Inference

```python
results = model(rgb_frame, verbose=False, conf=0.45)
```

- Input: RGB numpy array at the camera's native resolution (captured and flipped for mirror effect before being passed in)
- Confidence threshold: **0.45** — detections below this score are ignored
- NMS (Non-Maximum Suppression) is applied automatically by the Ultralytics runtime, so each face produces exactly one bounding box

### Output format

`detect(frame)` returns:

```python
detections : list of (x, y, w, h, status)
has_face   : bool
```

Where `(x, y)` is the top-left corner, `(w, h)` is width/height in pixels (camera-resolution space), and `status` is either `"mask"` or `"no_mask"`.

---

## 2. Person Tracker — `tracker.py`

Because YOLO runs on every inference frame independently, the same physical person would be counted multiple times without a tracking layer. `PersonTracker` solves this.

### Algorithm — Hungarian matching

Each inference frame, the tracker runs:

1. Compute the centroid `(cx, cy)` of every active track and every new detection
2. Build an N×M cost matrix of Euclidean distances (tracks × detections)
3. Run `scipy.optimize.linear_sum_assignment` (Hungarian algorithm) to find the globally optimal 1-to-1 assignment
4. Accept a match only if the distance is below `MAX_DIST = 100 px`
5. Unmatched tracks age out; unmatched detections start new tracks

### Track lifecycle

```
Detection arrives
        │
        ▼
   New _Track created (unconfirmed, total_frames = 1)
        │
        ▼  matched again (total_frames ≥ 2)
   Track confirmed
        │
        ├── matched each frame → bbox updated, mask_frames incremented
        │
        └── not matched for MAX_MISSED = 20 frames (~4 s at 5 fps)
                │
                ▼
           Track finalized → counted once as masked or unmasked
```

### Tuning constants

| Constant | Value | Purpose |
|---|---|---|
| `MAX_MISSED` | 20 frames | Frames without a match before a track is finalized |
| `MAX_DIST` | 100 px | Max centroid distance for a valid match (camera-res pixels) |
| `MIN_FRAMES` | 2 | Minimum matches before a track is "confirmed" (filters spurious detections) |
| `RE_ENTRY_DIST` | 120 px | Radius around an exit point that triggers re-entry suppression |
| `RE_ENTRY_SECS` | 30.0 s | How long an exit point is remembered |

### Mask status — majority vote

A finalized track is classified as **masked** if more than half its detected frames showed a mask:

```
is_masked = mask_frames > total_frames / 2
```

This prevents a single bad detection frame from flipping the result.

### Re-entry suppression

Without suppression, a person who briefly steps out of frame would be counted again when they return. The tracker prevents this:

1. When a confirmed track is finalized, its last centroid is stored in `_exit_memory` with a timestamp
2. When a new detection arrives, its centroid is compared against all stored exit points
3. If the distance is less than `RE_ENTRY_DIST` **and** the exit was within `RE_ENTRY_SECS`, the new track is flagged `re_entry = True`
4. `re_entry` tracks are never added to the count and never stored in `_finalized`

Exit points expire automatically after `RE_ENTRY_SECS = 30` seconds, so a person who genuinely returns after a long absence is counted again.

### Coordinate space

Detection coordinates are always in **original camera resolution** (e.g. 640×480, horizontally flipped for mirror display). The frame is **not** resized before inference. This ensures re-entry suppression works correctly even when the display window is resized, because the pixel coordinates stored in `_exit_memory` remain stable.

Bounding boxes are scaled to canvas size only when drawing on the display image:

```python
sx = canvas_width  / orig_width
sy = canvas_height / orig_height
xd, yd = int(x * sx), int(y * sy)
```

---

## 3. Threading model

YOLO inference is too slow to run synchronously in the Tkinter event loop (~5 fps on CPU vs 67 fps display). The dashboard uses a producer/consumer pattern:

```
Display loop (15 ms)          Inference thread (daemon)
─────────────────────         ──────────────────────────
read camera frame             wait on _det_queue
flip + put in queue  ──────►  run YOLO
resize for display            store result in _det_result
check for new result ◄──────  increment _det_id
  if new: update tracker
  draw bboxes on display_img
show frame
schedule next loop
```

- `_det_queue` has `maxsize=1` — if the thread is still busy, the display loop drops the frame (non-blocking `put_nowait`)
- `_det_id` / `_counted_id` ensure the tracker is updated exactly once per inference result
- Setting `_inference_active = False` stops the thread cleanly on `stop_camera()`

---

## 4. Unique person count

| Event | Action |
|---|---|
| Person enters frame | New track created (unconfirmed) |
| Person stays in frame | Track confirmed after 2 frames; mask vote accumulates |
| Person briefly disappears | Track ages; finalized after 20 missed frames |
| Finalized track | Added to `masked` or `unmasked` counter |
| Person re-enters within 30 s | New track flagged `re_entry`, not counted |
| Camera stopped | All remaining active confirmed tracks finalized and counted |
| Total Persons | `masked + unmasked` at session end |
