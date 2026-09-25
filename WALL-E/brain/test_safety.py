"""Tests for the invariants that keep the personality layer harmless.

Run:  python3 test_safety.py       (no pytest needed)
  or: pytest test_safety.py

These are not unit tests in the usual sense. They are checks that the safety
argument in docs/01-architecture.md still holds after somebody edits the code.
If one of these fails, do not adjust the test — the thing it is protecting has
been broken.
"""

from __future__ import annotations

import time

from perception import Person, Snapshot
from personality import Action, Personality, motion_for, _MOTION


# The Spine caps the Brain at 25% duty (DUTY_MAX_ASSIST in
# firmware/spine/config.h). The personality must stay inside that on its own,
# so the cap is a backstop and not the only limit.
BRAIN_MOTION_CEILING = 0.30


def test_every_action_has_a_bounded_motion():
    """No action, present or future, may ask for more than the ceiling."""
    for action in Action:
        m = motion_for_action(action)
        assert abs(m.speed) <= BRAIN_MOTION_CEILING, \
            f"{action.value} asks for speed {m.speed}"
        assert abs(m.turn) <= BRAIN_MOTION_CEILING, \
            f"{action.value} asks for turn {m.turn}"


def test_no_action_is_missing_from_the_motion_table():
    """A new Action with no table entry must not silently become zero.

    It would be safe, but it would be a bug that hides itself: the behaviour
    would be added, chosen, logged, and do nothing at all.
    """
    missing = [a.value for a in Action if a not in _MOTION]
    assert not missing, f"actions with no motion defined: {missing}"


def test_forward_motion_is_slower_than_reverse_is_not_assumed():
    """Retreating must actually reverse, not creep forward.

    Worth a test because a sign error here turns "back away from the person
    who got too close" into "drive at them".
    """
    assert motion_for_action(Action.RETREAT).speed < 0


def test_follow_turn_stays_inside_the_ceiling():
    from personality import Intent
    wild = Intent(Action.FOLLOW, gaze_az=180.0)
    m = motion_for(wild)
    assert abs(m.speed) <= BRAIN_MOTION_CEILING
    assert abs(m.turn) <= BRAIN_MOTION_CEILING
    assert m.speed > 0


def test_follow_requires_may_move():
    p = Personality()
    snap = Snapshot()
    snap.people = [Person(az_deg=10.0, el_deg=0.0, distance_m=2.5,
                          confidence=0.9)]
    snap.people_at = time.monotonic()
    for _ in range(40):
        intent = p.update(snap, may_move=False)
        assert intent.action != Action.FOLLOW
        m = motion_for(intent)
        assert m.speed == 0.0 and m.turn == 0.0
        p._until = 0.0


def test_close_person_never_nudges_forward():
    """Garden wander must not walk into a face that is already too close."""
    p = Personality()
    snap = Snapshot()
    snap.people = [Person(az_deg=0.0, el_deg=0.0, distance_m=0.8,
                          confidence=0.9)]
    snap.people_at = time.monotonic()
    for _ in range(40):
        intent = p.update(snap, may_move=True)
        assert intent.action != Action.NUDGE_FORWARD
        assert intent.action != Action.FOLLOW
        p._until = 0.0


def test_personality_requests_nothing_when_movement_is_blocked():
    """With may_move False, the chooser must not pick a moving action."""
    p = Personality()
    snap = Snapshot()
    snap.people = [Person(az_deg=5.0, el_deg=0.0, distance_m=0.8,
                          confidence=0.9)]
    snap.people_at = time.monotonic()

    for _ in range(50):
        intent = p.update(snap, may_move=False)
        m = motion_for(intent)
        assert m.speed == 0.0 and m.turn == 0.0, \
            f"{intent.action.value} asked to move while blocked"
        # skip past the dwell so the chooser runs again
        p._until = 0.0


def test_stale_perception_yields_no_person():
    """An old camera reading must not look like a current one.

    This is the failure that matters: a camera that froze with a person in
    frame must not leave the robot reacting to someone who has walked away.
    """
    snap = Snapshot()
    snap.people = [Person(az_deg=0.0, el_deg=0.0, distance_m=2.0,
                          confidence=0.9)]
    snap.people_at = time.monotonic() - 10.0
    assert snap.nearest_person is None


def test_low_confidence_person_is_ignored():
    snap = Snapshot()
    snap.people = [Person(az_deg=0.0, el_deg=0.0, distance_m=2.0,
                          confidence=0.2)]
    snap.people_at = time.monotonic()
    assert snap.nearest_person is None


# ---------------------------------------------------------------------------
def motion_for_action(action: Action):
    from personality import Intent
    return motion_for(Intent(action))


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
    print("all invariants hold" if not failures else f"{failures} FAILED")
    raise SystemExit(1 if failures else 0)
