# 06 — Why the batteries are low, and how the box keeps sand out

Asked on 2026-09-16: why can't the batteries be inside the body? The reason
behind the question was sand. The packs need to be in a closed box.

**The question found a real bug.** The box I had drawn was a three-sided U —
a floor and two side walls that stopped at the rail top, 15 mm *below* the tops
of the packs. It was open across the top, open at both ends, and it had four
Ø30 mm spanner holes in the sides. It hangs directly inboard of the belts, and
the belts throw sand inward and upward. Sand would have filled it in a day.

That is fixed. The box is now a closed, gasketed box, and the cut list has the
end walls and the lid in it. Section 1 is the specification.

The location question then still stands, and section 2 answers it: seal the low
box rather than move the packs up.

---

## 1. The closed box

Run `cad/walle_frame.scad` and the cut list prints all six panels.

| Panel | Size | Notes |
|---|---|---|
| Floor | 444 × 240 | 12 mm ply |
| Lid | 444 × 240 | 12 mm ply, 12 × M5 round the edge at 110 mm pitch |
| Side walls | 2 × 444 × 142 | Each with 2 × Ø30 spanner holes, 77 mm up |
| End walls | 2 × 240 × 142 | **These are the new parts. They close the box** |

The walls are 142 mm tall now, not 107, so they reach above the packs and the
lid has something to seal against.

### The four things that actually make it sealed

**A gasket, and enough bolts to squeeze it.** 3 mm closed-cell foam tape under
the lid. Twelve M5 bolts at 110 mm pitch, which is closer than it looks like it
needs to be — a gasket only seals where it is squeezed, so a bolt every 250 mm
leaves the middle of each span open.

**Plugs in the spanner holes.** The four Ø30 holes are how you reach the M12
bolts that hold the pods on, so they have to stay. But they are holes in a
sealed box and they point at the belts. Each gets a silicone blanking plug, in
place whenever you are not removing a pod. They cost about a dollar each and
without them none of the rest of this matters.

**A foam pad on top of the packs.** 8 mm of closed-cell foam between the packs
and the lid. It clamps the packs down so they cannot move, and it takes the
vibration that would otherwise go straight into the cells.

**A membrane vent — this one is not optional.** A fully sealed box *breathes*.
The desert swings from about 15 °C at night to 40 °C in the day, and the air
inside expands and contracts with it. Every cycle pushes air out and pulls air
back in, and it pulls it through whichever leak is worst. Seal a box perfectly
and you have built a dust pump.

A screw-in membrane vent (the Gore type) gives that air a deliberate path that
passes air but not dust or water. It goes in the **lid**, on the centreline,
directly over the 24 mm gap between the two packs so the foam pad does not block
the airway. The lid is the most sheltered surface on the box: the body floor
sits 43 mm above it, so nothing has a straight path to it.

There is a second reason the vent goes in the lid. There is barely any wall
above the packs to put it in — the model's guards catch this, and the first
attempt put it 2 mm *below* the pack tops.

### Charge the packs in place. Do not take them out

Once the box is sealed, **every time you open it you undo the sealing.** At a
dusty event, opening the pack box daily is worse than never sealing it.

So the packs are not removable in the field. Run the charge leads out of the box
through a cable gland, to a connector on the outside of the body behind a dust
cap, and charge the robot without opening anything. This is how every e-bike and
scooter with an integrated pack works.

The box opens for maintenance only, which means lifting the body off first. That
is a workshop job, not a field job, and that is the right trade.

> One thing to check on the bench: charging inside a sealed box has nowhere to
> put the heat. At 5 A a 48 V pack loses roughly 12 W as heat. Measure the pack
> temperature through a full charge with the lid on before trusting it, and if it
> climbs, charge with the body lid open or drop the charge current.

---

## 2. Why seal the low box, instead of moving the packs into the body

On sand alone, the body looks like the better place: it is higher up, closed, and
away from the belts. That is a fair point, so here is the argument against it.

**The packs need a sealed case wherever they go.** Putting them in the body does
not remove that work. The body is not a clean environment — it has a filtered air
intake, a removable top lid and several cable entries, and it is full of
electronics that you would not want a cell to vent next to. They would still end
up in their own gasketed case, just a case sitting higher up. The sealing work in
section 1 happens either way.

Once that is true, the location is decided by everything else, and low wins on
all of it:

**The body is the hottest place on the robot.** Inside it there is a Jetson
putting out 25 W, both VESCs and the amplifier, in a sealed foam-lined box, in
the Negev. Lithium cells lose life quickly above 45 °C, and that is normal
ageing, not a fault. Under the frame the packs sit in open air in the draught of
driving — the best-cooled spot on the machine, free.

**The shelf cannot really take them.** A pack is 400 mm long and the shelf is
only 356 mm deep, so they could not even lie fore-aft. Lying across the robot the
two of them use 50 % of the shelf area on top of the 32 % the electronics already
need. That is 83 % of the shelf, and what is left has to hold two 6.5 inch
speakers and a clear air path.

**It is the worst place for a cell to fail.** A box under the frame vents
downwards and away from everything. The same event on the electronics shelf
happens inside the body, next to every board, with the head on top of it.

**It throws away the best volume on the robot.** The frame interior is
444 × 240 × 110 mm, lower than anything else, and mass down there *improves* the
tipping instead of hurting it.

### The tipping numbers, for completeness

| | Battery CoM | Robot CoM | Tips forward at |
|---|---|---|---|
| **As built** — packs in the frame | 217 mm | 332 mm | **19.2°** |
| If moved to the body shelf | 399 mm | 364 mm | 17.6° |

Moving them up raises the centre of mass 32 mm and costs 1.6°. **That on its own
is not a veto, and it is worth being honest about that** — the anti-tip castor
catches the pitch at 12.3° either way, so the margin would go from 6.9° to 5.3°
and still pass. Tipping is not the reason. The four points above are.

---

## 3. The one argument for moving them: ground clearance

The plywood box floor is the lowest point of the robot, at 150 mm. Remove the box
and the lowest point becomes the rail bottoms at 197 mm. That is 47 mm of extra
ground clearance, and on rutted sand it is a genuine gain.

If clearance turns out to be the problem, **do not solve it by moving the packs
into the body. Raise the box.** The pack top is at 272 mm and the pod belt crown
above it is at 327, so there is unused headroom. The limit is not the crown — it
is the M12 spanner holes in the side walls, which have to stay clear of the
floor. That caps the floor at 190 mm. Checked against the model: at 190 the guard
sits exactly on its minimum, and at 195 it fails.

| | Ground clearance | Robot CoM | Tips forward at |
|---|---|---|---|
| Box floor at 150 (as built) | 150 mm | 332 mm | 19.2° |
| Box floor at 190 (the limit) | **190 mm** | 340 mm | **18.8°** |
| Packs in the body | 197 mm | 364 mm | 17.6° |

Raising the box buys 40 of the 47 mm for 0.4° instead of 1.6°, and none of the
heat, access or failure-mode problems. Owner decision 2026-09-16: leave it at
150 for now and revisit after the first drive on sand.

One consequence to design for if it does get raised: at a floor of 190 the side
walls are only 60 mm of useful depth below the rail top, so the packs stand
proud of the rails by more. The lid bolts then need blocks to land on rather than
just the wall edges.

---

## Summary

The box was open, which was a real fault, and it is now a closed box with a
gasket, plugged spanner holes, a foam pad and a membrane vent in the lid. Charge
through a sealed connector and do not open it in the field.

Keep the packs low. Not because of the tipping, which is affordable, but because
they need a sealed case wherever they go, and once that is true the body is the
hottest, most crowded, and most dangerous place to put them.
