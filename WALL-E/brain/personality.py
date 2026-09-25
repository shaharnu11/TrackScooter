"""The personality layer.

This is the part people came to see, and it is also the part that must never be
allowed near a motor number.

The rule
--------
The personality chooses an ACTION from a short fixed list. A plain, boring,
readable function turns that action into a speed and a turn. The chooser can be
a state machine, or later a language model, and it makes no difference to the
safety argument, because the chooser cannot express anything except one of
these names.

    idle · look_at · greet · retreat · nudge_forward · follow · play_sound

An LLM asked "what should WALL-E do?" can answer "greet". It cannot answer
"0.8 duty for 4 seconds", because there is no way to say that in this
vocabulary. That is what makes it safe to put a language model on a machine
that weighs 91 kg.

See WALL-E/docs/01-architecture.md section 5.
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from enum import Enum

from perception import Snapshot

log = logging.getLogger(__name__)


class Action(str, Enum):
    IDLE = "idle"
    LOOK_AT = "look_at"
    GREET = "greet"
    RETREAT = "retreat"
    NUDGE_FORWARD = "nudge_forward"
    FOLLOW = "follow"
    PLAY_SOUND = "play_sound"


@dataclass(frozen=True)
class Intent:
    """What the personality wants. Note there is no duty cycle in here."""

    action: Action
    gaze_az: float = 0.0        # degrees, where to look
    gaze_el: float = 0.0
    mood: str = "idle"
    sound: str | None = None


@dataclass(frozen=True)
class Motion:
    """The movement request that comes out of an Intent. -1..+1 each."""

    speed: float = 0.0
    turn: float = 0.0


# How much movement each action is allowed to ask for. These are the ONLY
# numbers in the program that turn a feeling into motion, which is why they all
# live in one table where they can be reviewed at a glance.
#
# Everything is small. The Spine caps the Brain at 25% duty anyway
# (DUTY_MAX_ASSIST in firmware/spine/config.h), so these are a second,
# independent limit — not the only one.
_MOTION: dict[Action, Motion] = {
    Action.IDLE:          Motion(0.00,  0.00),
    Action.LOOK_AT:       Motion(0.00,  0.00),   # eyes only. Body stays put.
    Action.GREET:         Motion(0.00,  0.00),   # sound and eyes, no movement
    Action.RETREAT:       Motion(-0.30, 0.00),   # back away, slowly
    Action.NUDGE_FORWARD: Motion(0.25,  0.00),
    Action.FOLLOW:        Motion(0.20,  0.00),  # turn comes from gaze, clamped below
    Action.PLAY_SOUND:    Motion(0.00,  0.00),
}

_FOLLOW_SPEED = 0.20
_FOLLOW_TURN = 0.20
_FOLLOW_AZ = 45.0  # degrees of error that asks for full _FOLLOW_TURN


def motion_for(intent: Intent) -> Motion:
    """Turn an Intent into a Motion.

    All actions except follow are a table lookup. Follow is the same slow
    forward speed, plus a turn toward the person, clamped so it cannot
    exceed the Brain ceiling.
    """
    if intent.action is Action.FOLLOW:
        turn = intent.gaze_az / _FOLLOW_AZ * _FOLLOW_TURN
        turn = max(-_FOLLOW_TURN, min(_FOLLOW_TURN, turn))
        return Motion(_FOLLOW_SPEED, turn)
    return _MOTION.get(intent.action, Motion())


class Personality:
    """A plain state machine. Replace the chooser, keep the vocabulary."""

    # How long each action runs before we reconsider. Stops the robot
    # twitching between behaviours every 50 ms.
    _DWELL_S = {
        Action.IDLE: 2.5,
        Action.LOOK_AT: 1.2,
        Action.GREET: 3.0,
        Action.RETREAT: 1.5,
        Action.NUDGE_FORWARD: 1.0,
        Action.FOLLOW: 0.4,
        Action.PLAY_SOUND: 2.0,
    }

    def __init__(self) -> None:
        self._action = Action.IDLE
        self._until = 0.0
        self._last_greet = 0.0
        self._intent = Intent(Action.IDLE)

    def update(self, snap: Snapshot, *, may_move: bool) -> Intent:
        """Pick an intent. Called every control loop pass.

        `may_move` is false whenever the robot is not allowed to move — wrong
        mode, a fault, pitched too far forward. When it is false the chooser is
        restricted to actions that ask for no movement, so the personality
        simply cannot request motion it will not be given. That keeps the log
        honest: you never see a rejected movement request, because none was
        made.
        """
        now = time.monotonic()
        if now < self._until:
            return self._refresh_gaze(self._intent, snap)

        self._action = self._choose(snap, now, may_move=may_move)
        self._until = now + self._DWELL_S[self._action]
        self._intent = self._build(self._action, snap, now)
        log.info("personality -> %s", self._action.value)
        return self._intent

    # -- the chooser. This is the part an LLM could replace. ---------------
    # Garden ASSIST only. Radio ON. Sticks centred. Spine still owns stop.
    # He never picks a motor number — only these names. Nudge is 1 s at 25%.
    _CLOSE_M = 1.2
    _FOLLOW_MIN_M = 1.5
    _FOLLOW_MAX_M = 4.0
    _NUDGE_P = 0.25
    _CHIRP_P = 0.15

    def _choose(self, snap: Snapshot, now: float, *, may_move: bool) -> Action:
        close = snap.nearest_person
        person = snap.focus_person

        if close is not None and close.distance_m < self._CLOSE_M:
            return Action.RETREAT if may_move else Action.GREET

        if person is None:
            if may_move and random.random() < self._NUDGE_P:
                return Action.NUDGE_FORWARD
            return Action.PLAY_SOUND if random.random() < self._CHIRP_P else Action.IDLE

        if (may_move
                and self._FOLLOW_MIN_M <= person.distance_m <= self._FOLLOW_MAX_M):
            return Action.FOLLOW

        # Greeting is rate limited, or he does it to the same person forever.
        if person.distance_m < 3.0 and (now - self._last_greet) > 12.0:
            self._last_greet = now
            return Action.GREET

        return Action.LOOK_AT

    def _build(self, action: Action, snap: Snapshot, now: float) -> Intent:
        if action is Action.RETREAT:
            person = snap.nearest_person
        else:
            person = snap.focus_person
        az = person.az_deg if person else 0.0
        el = person.el_deg if person else 0.0

        if action is Action.GREET:
            return Intent(action, az, el, mood="happy", sound="greet")
        if action is Action.LOOK_AT:
            return Intent(action, az, el, mood="curious")
        if action is Action.RETREAT:
            return Intent(action, az, el, mood="alarm")
        if action is Action.PLAY_SOUND:
            return Intent(action, az, el, mood="idle", sound="chirp")
        if action is Action.NUDGE_FORWARD:
            return Intent(action, az, el, mood="curious")
        if action is Action.FOLLOW:
            return Intent(action, az, el, mood="curious")
        return Intent(Action.IDLE, 0.0, 0.0, mood="idle")

    def _refresh_gaze(self, intent: Intent, snap: Snapshot) -> Intent:
        """Keep tracking a person while the action itself is still running.

        The eyes update at the full loop rate even though the action is held,
        so he follows you continuously instead of snapping every 1.2 seconds.
        """
        if intent.action is Action.RETREAT:
            person = snap.nearest_person
        else:
            person = snap.focus_person
        if person is None:
            return intent
        return Intent(intent.action, person.az_deg, person.el_deg,
                      intent.mood, intent.sound)
