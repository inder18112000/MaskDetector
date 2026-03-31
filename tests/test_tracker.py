"""
Tests for app/camera/tracker.py — person tracking algorithm.

These tests exercise the pure logic of the tracker without a camera or GUI.

Run with:  pytest tests/test_tracker.py -v
"""

import pytest
from app.camera.tracker import PersonTracker


# ── helpers ───────────────────────────────────────────────────────────────────

MASKED   = "mask"
UNMASKED = "no_mask"


def _det(x=100, y=100, w=50, h=60, status=MASKED):
    """Return a detection tuple (x, y, w, h, status)."""
    return (x, y, w, h, status)


def _run_frames(tracker, detection_list, n_frames: int):
    """Feed a fixed list of detections for *n_frames* frames."""
    for _ in range(n_frames):
        tracker.update(detection_list)


# ── basic tracking ─────────────────────────────────────────────────────────────

class TestTrackerBasics:
    def test_empty_frame_no_tracks(self):
        t = PersonTracker()
        t.update([])
        assert t.get_finalized() == []
        assert t.get_active() == []

    def test_single_detection_creates_active_track(self):
        t = PersonTracker()
        _run_frames(t, [_det()], 3)   # MIN_FRAMES=2, so 3 frames confirms
        assert len(t.get_active()) == 1

    def test_track_confirmed_after_min_frames(self):
        t = PersonTracker()
        _run_frames(t, [_det()], 2)
        active = t.get_active()
        assert len(active) == 1
        assert active[0].confirmed is True

    def test_unconfirmed_track_not_in_active(self):
        """A track seen only once should not be confirmed yet."""
        t = PersonTracker()
        t.update([_det()])
        active = t.get_active()
        assert all(not tr.confirmed for tr in active)

    def test_track_finalizes_after_disappearing(self):
        t = PersonTracker()
        _run_frames(t, [_det()], 5)          # confirm the person
        _run_frames(t, [], 25)               # disappear for > MAX_MISSED frames
        finalized = t.get_finalized()
        assert len(finalized) == 1

    def test_finalized_track_cleared_after_get(self):
        t = PersonTracker()
        _run_frames(t, [_det()], 5)
        _run_frames(t, [], 25)
        t.get_finalized()                    # first call returns the track
        assert t.get_finalized() == []       # second call is empty


# ── mask status logic ─────────────────────────────────────────────────────────

class TestMaskStatus:
    def test_majority_masked_frames_is_masked(self):
        t = PersonTracker()
        # 4 masked frames, then 1 unmasked, then disappear
        _run_frames(t, [_det(status=MASKED)], 4)
        _run_frames(t, [_det(status=UNMASKED)], 1)
        _run_frames(t, [], 25)
        tracks = t.get_finalized()
        assert len(tracks) == 1
        assert tracks[0].is_masked is True

    def test_majority_unmasked_frames_is_unmasked(self):
        t = PersonTracker()
        _run_frames(t, [_det(status=UNMASKED)], 5)
        _run_frames(t, [_det(status=MASKED)],   1)
        _run_frames(t, [], 25)
        tracks = t.get_finalized()
        assert len(tracks) == 1
        assert tracks[0].is_masked is False


# ── multiple people ────────────────────────────────────────────────────────────

class TestMultiplePeople:
    def test_two_separate_persons_tracked(self):
        t = PersonTracker()
        d1 = _det(x=50,  y=50,  status=MASKED)
        d2 = _det(x=500, y=50,  status=UNMASKED)  # far from d1
        _run_frames(t, [d1, d2], 5)
        assert len(t.get_active()) == 2

    def test_two_persons_finalize_independently(self):
        t = PersonTracker()
        d1 = _det(x=50,  y=50,  status=MASKED)
        d2 = _det(x=500, y=500, status=UNMASKED)
        _run_frames(t, [d1, d2], 5)
        _run_frames(t, [], 25)
        finalized = t.get_finalized()
        assert len(finalized) == 2
        statuses = {tr.is_masked for tr in finalized}
        assert statuses == {True, False}


# ── reset ──────────────────────────────────────────────────────────────────────

class TestReset:
    def test_reset_clears_all_state(self):
        t = PersonTracker()
        _run_frames(t, [_det()], 5)
        t.reset()
        assert t.get_active()    == []
        assert t.get_finalized() == []

    def test_tracking_works_after_reset(self):
        t = PersonTracker()
        _run_frames(t, [_det()], 5)
        t.reset()
        _run_frames(t, [_det(x=200, y=200)], 5)
        assert len(t.get_active()) == 1
