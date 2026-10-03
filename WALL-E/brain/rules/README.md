# WALL-E's rules

How he must behave, in every personality. Read at start-up and added to his
instructions **after** the personality, which is told: if anything in it
conflicts with these rules, the rules win.

- The owner changes them by voice in management mode ("answers can be up to
  three sentences"): read back, saved on "yes", the old file in `history/`.
  Or by hand.
- These are soft rules, instructions to the brain: it almost always follows
  them. The hard rules live only in code and cannot be changed by voice: sentence limit, filters
  (walle/mind/chat.py), owner/visitor checks and tools (walle/talker.py,
  walle/modes/), consent (walle/people/persons.py).
- `<!-- comments -->` and `#` headings are not sent to the brain.

| File | When |
|---|---|
| always.md | always |
| english.md / hebrew.md | by --lang |
| eyes_picture.md | the brain sees camera pictures (Qwen3-VL) |
| eyes_described.md | the brain gets the picture as words (Hebrew: DictaLM + eyes) |
| eyes_none.md | no camera pictures |
