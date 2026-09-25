"""Speaker lock: look at the talker, not the nearest bystander."""

from __future__ import annotations

from perception import Person
from speaker_lock import HOLD_S, SpeakerLock


def _p(track_id, dist, speaking, az=0.0):
    return Person(
        az_deg=az, el_deg=0.0, distance_m=dist,
        confidence=0.9, track_id=track_id, speaking=speaking,
    )


def test_lock_picks_the_talker_not_the_nearest():
    lock = SpeakerLock()
    near = _p(1, 1.5, False)
    talk = _p(2, 3.0, True, az=20.0)
    sid = lock.update([near, talk], now=10.0)
    assert sid == 2


def test_lock_holds_through_a_side_shout():
    lock = SpeakerLock()
    a = _p(1, 2.0, True)
    lock.update([a], now=1.0)
    a_quiet = _p(1, 2.0, False)
    shout = _p(2, 1.6, True, az=25.0)
    sid = lock.update([a_quiet, shout], now=1.0 + HOLD_S / 2)
    assert sid == 1


def test_lock_drops_when_the_speaker_leaves():
    lock = SpeakerLock()
    a = _p(1, 2.0, True)
    lock.update([a], now=1.0)
    other = _p(2, 2.2, False, az=15.0)
    sid = lock.update([other], now=1.2)
    assert sid is None


def test_focus_person_is_the_locked_speaker():
    from perception import Snapshot
    import time

    snap = Snapshot()
    snap.people = [_p(1, 1.5, False), _p(2, 3.0, True, az=18.0)]
    snap.people_at = time.monotonic()
    snap.speaker_id = 2
    focus = snap.focus_person
    assert focus is not None
    assert focus.track_id == 2


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {name}: {e}")
    print()
    print("ok" if not failures else f"{failures} FAILED")
    raise SystemExit(1 if failures else 0)
