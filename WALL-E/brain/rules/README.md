# WALL-E's rules

How he must behave, in every personality. Read at start-up and added to his
instructions **after** the personality, which is told: if anything in it
conflicts with these rules, the rules win.

- Not editable by voice: "update personality" only changes
  `personalities/<lang>/<name>/personality.md`. Change these by hand.
- These are instructions to the brain (soft): it almost always follows them.
  The hard rules live in code (talk_english.py, persona_edit.py, persons.py,
  manage.py): sentence limit, filters, owner checks, consent, tools.
- `<!-- comments -->` and `#` headings are not sent to the brain.

| File | When |
|---|---|
| always.md | always |
| english.md / hebrew.md | by --lang |
| eyes_picture.md | the brain sees camera pictures (Qwen3-VL) |
| eyes_described.md | the brain gets the picture as words (Hebrew: DictaLM + eyes) |
| eyes_none.md | no camera pictures |
