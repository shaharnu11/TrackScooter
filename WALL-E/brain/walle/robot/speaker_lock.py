"""Lock gaze on the person who is talking.

The microphone hears a mix. The camera sees mouths. Once a speaker is chosen,
keep them until they go quiet for a short hold, so a shout from the side does
not steal the eyes.
"""

from __future__ import annotations

from dataclasses import dataclass

HOLD_S = 1.5


@dataclass
class SpeakerLock:
    track_id: int | None = None
    until: float = 0.0

    def update(self, people, now: float) -> int | None:
        by_id = {p.track_id: p for p in people}
        if self.track_id is not None:
            cur = by_id.get(self.track_id)
            if cur is None:
                self.track_id = None
            elif cur.speaking:
                self.until = now + HOLD_S
                return self.track_id
            elif now < self.until:
                return self.track_id
            else:
                self.track_id = None

        talking = [p for p in people if p.speaking and p.interesting]
        if not talking:
            return self.track_id
        pick = min(talking, key=lambda p: p.distance_m)
        self.track_id = pick.track_id
        self.until = now + HOLD_S
        return self.track_id
