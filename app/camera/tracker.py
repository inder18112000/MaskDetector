"""
Person tracker for mask-detection surveillance.

Each unique person who passes through the camera view is counted exactly once.
Uses Hungarian-algorithm matching (scipy.optimize.linear_sum_assignment) on
Euclidean centroid distances — no extra pip installs required.

Mask status per person is determined by majority vote:
  mask_frames / total_frames > 0.5  →  counted as masked

Re-entry suppression:
  When a track is finalized its exit centroid is remembered for RE_ENTRY_SECS
  seconds.  If a new detection appears within RE_ENTRY_DIST pixels of that exit
  point the new track is marked as a re-entry and NOT counted again — preventing
  the same physical person from inflating the total when they briefly step out
  of frame and back in.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment

# ── Tuning constants ──────────────────────────────────────────────────────────
MAX_MISSED      = 20   # inference frames without a match before finalising (~4 s at 5 fps)
MAX_DIST        = 100  # max centroid-to-centroid pixel distance for a valid match
MIN_FRAMES      = 2    # a track must match at least this many times to be "confirmed"
RE_ENTRY_DIST   = 120  # px radius around an exit point that triggers re-entry suppression
RE_ENTRY_SECS   = 30.0 # seconds to remember an exit point
# ─────────────────────────────────────────────────────────────────────────────

MASKED   = "mask"
UNMASKED = "no_mask"


@dataclass
class _Track:
    """Internal state for a single tracked person."""
    id:           int
    bbox:         tuple          # (x, y, w, h)
    mask_frames:  int  = 0
    total_frames: int  = 0
    missed:       int  = 0
    confirmed:    bool = False   # True after MIN_FRAMES consecutive matches
    re_entry:     bool = False   # True if this track started near a recent exit point

    @property
    def centroid(self) -> tuple[float, float]:
        x, y, w, h = self.bbox
        return (x + w / 2, y + h / 2)

    @property
    def is_masked(self) -> bool:
        """Majority-vote mask status."""
        if self.total_frames == 0:
            return False
        return self.mask_frames > self.total_frames / 2


class PersonTracker:
    """
    Assign stable IDs to detected faces across inference frames and count
    each unique person exactly once.

    Typical usage inside the dashboard update loop:

        tracker.update(detections)          # list of (x,y,w,h,status)
        for t in tracker.get_finalized():   # persons who left the scene
            if t.is_masked: masked_count += 1
            else:           unmasked_count += 1

    At stop_camera(), also drain active tracks:
        for t in tracker.get_active() + tracker.get_finalized():
            ...
    """

    def __init__(self) -> None:
        self._tracks:      dict[int, _Track]              = {}
        self._next_id:     int                            = 0
        self._finalized:   list[_Track]                   = []
        # (cx, cy, timestamp) — exit points remembered for re-entry suppression
        self._exit_memory: list[tuple[float, float, float]] = []

    # ── public API ────────────────────────────────────────────────────────────

    def update(self, detections: list) -> None:
        """
        Process one batch of YOLO detections for the current inference frame.

        Parameters
        ----------
        detections : list of (x, y, w, h, status_str)
            As returned by mask_detector.detect().
        """
        track_list = list(self._tracks.values())

        if not track_list:
            for det in detections:
                self._new_track(det)
            return

        if not detections:
            self._age_tracks(matched_ids=set())
            return

        # Build cost matrix: rows = tracks, cols = detections
        n_t = len(track_list)
        n_d = len(detections)
        cost = np.zeros((n_t, n_d), dtype=np.float32)
        for i, track in enumerate(track_list):
            for j, det in enumerate(detections):
                cost[i, j] = _centroid_dist(track.centroid, det)

        row_ind, col_ind = linear_sum_assignment(cost)

        matched_track_ids: set[int] = set()
        matched_det_indices: set[int] = set()

        for r, c in zip(row_ind, col_ind):
            if cost[r, c] < MAX_DIST:
                track = track_list[r]
                det   = detections[c]
                track.bbox         = det[:4]
                track.total_frames += 1
                if det[4] == MASKED:
                    track.mask_frames += 1
                track.missed = 0
                if track.total_frames >= MIN_FRAMES:
                    track.confirmed = True
                matched_track_ids.add(track.id)
                matched_det_indices.add(c)

        self._age_tracks(matched_ids=matched_track_ids)

        for j, det in enumerate(detections):
            if j not in matched_det_indices:
                self._new_track(det)

    def get_finalized(self) -> list[_Track]:
        """Return confirmed, non-re-entry tracks that have left the scene, then clear."""
        done = self._finalized[:]
        self._finalized.clear()
        return done

    def get_active(self) -> list[_Track]:
        """Return confirmed, non-re-entry active tracks."""
        return [t for t in self._tracks.values() if t.confirmed and not t.re_entry]

    def reset(self) -> None:
        """Clear all state. Call at the start of each new camera session."""
        self._tracks.clear()
        self._finalized.clear()
        self._exit_memory.clear()
        self._next_id = 0

    # ── internals ─────────────────────────────────────────────────────────────

    def _new_track(self, det: tuple) -> None:
        x, y, w, h, status = det
        cx = x + w / 2
        cy = y + h / 2

        # Prune stale exit points
        now = time.monotonic()
        self._exit_memory = [
            (ex, ey, et) for ex, ey, et in self._exit_memory
            if now - et < RE_ENTRY_SECS
        ]

        # Check if this detection is a re-entry near a recent exit point
        re_entry = any(
            math.hypot(cx - ex, cy - ey) < RE_ENTRY_DIST
            for ex, ey, _ in self._exit_memory
        )

        t = _Track(
            id           = self._next_id,
            bbox         = (x, y, w, h),
            mask_frames  = 1 if status == MASKED else 0,
            total_frames = 1,
            re_entry     = re_entry,
        )
        self._tracks[self._next_id] = t
        self._next_id += 1

    def _age_tracks(self, matched_ids: set[int]) -> None:
        to_remove = []
        for tid, track in self._tracks.items():
            if tid in matched_ids:
                continue
            track.missed += 1
            if track.missed >= MAX_MISSED:
                to_remove.append(tid)
                if track.confirmed:
                    if not track.re_entry:
                        # Record exit point for future re-entry suppression
                        cx, cy = track.centroid
                        self._exit_memory.append((cx, cy, time.monotonic()))
                        self._finalized.append(track)
                    # re_entry confirmed tracks are silently discarded
                # Unconfirmed tracks are always silently discarded
        for tid in to_remove:
            del self._tracks[tid]


# ── helpers ───────────────────────────────────────────────────────────────────

def _centroid_dist(centroid: tuple[float, float], det: tuple) -> float:
    """Euclidean distance between an existing track centroid and a new detection."""
    x, y, w, h = det[:4]
    det_cx = x + w / 2
    det_cy = y + h / 2
    return math.hypot(centroid[0] - det_cx, centroid[1] - det_cy)
