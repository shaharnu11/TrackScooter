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
| Floor | 444 × 268 | 12 mm ply |
| Lid | 444 × 268 | 12 mm ply, 12 × M5 round the edge at 110 mm pitch |
| Side walls | 2 × 444 × 142 | Each with 2 × Ø30 spanner holes, 77 mm up |
| End walls | 2 × 268 × 142 | **These are the new parts. They close the box** |

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

### Charge in place every day. Lift a pack out when you need to

Opening the sealed box every morning in sand undoes the gasket. So the **daily**
charge path is still a connector on the body, behind a dust cap, without opening
anything. That is how you charge at the festival.

That must not trap the packs. **Every battery unplugs and lifts out** for a failed
BMS, a damaged case, or a charger that is not next to the robot. Owner, 2026-09-23.

**48 V traction packs.** The body floor sits 43 mm above the box lid, so packs do
not come out through the body. Unbolt the body from the four risers, unbolt the
twelve M5 lid bolts, unplug each pack's XT90-S and its charge pigtail, lift out.
The foam pad is a pad, not glue. The charge lead through the gland ends on a
connector on the pack — it is not soldered into the cells. After the pack goes
back in, replace the lid gasket if it tore, torque the M5s, check the four
spanner-hole plugs.

**12 V electronics pack and the PD pack.** Unbolt the speaker boxes, lift the
laptop tray, unplug, lift out. Both sit on straps, not on glue. The 12 V pack
has its own XT60; the PD pack unplugs USB-C.

**XPS.** The laptop (and its own cells) comes out with the tray.

**There are three body charge connectors**, plus the PD pack's USB-C. Decision D8
added the 12 V electronics battery. It lives on the shelf, not in this box. It
charges the same way — through its own connector on the body — but it takes a
**LiFePO4 charger at 14.6 V**, which is not the same charger as the 48 V packs
use. Label the three XT60s so that nobody puts 54.6 V into the 12 V one.

> One thing to check on the bench: charging inside a sealed box has nowhere to
> put the heat. At 5 A a 48 V pack loses roughly 12 W as heat. Measure the pack
> temperature through a full charge with the lid on before trusting it, and if it
> climbs, charge with the body off or drop the charge current. Taking a pack out
> to charge it is always allowed.

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

**The body is the hottest place on the robot.** Inside it there is a closed 15 inch laptop
putting out tens of watts, both motor controllers and the amplifier, in a plywood box, in
the Negev. Lithium cells lose life quickly above 45 °C, and that is normal
ageing, not a fault. Under the frame the packs sit in open air in the draught of
driving — the best-cooled spot on the machine, free.

**The shelf cannot really take them.** A pack is 400 mm long and the shelf is
only 356 mm deep, so they could not even lie fore-aft. Lying across the robot the
two of them use 50 % of the shelf area on top of the 40 % the electronics already
need. That is 90 % of the shelf, and what is left has to hold a clear air path
past the XPS and both motor controllers. It will not.

That figure has got worse twice since it was first written. The two speaker
enclosures sit over 54 % of the shelf. And decision D8 put the electronics
battery up there, which is what took the electronics from 32 % to 40 %. The shelf
is the scarcest area on the robot, and the traction packs are the last thing that
should compete for it.

**The electronics battery is not an argument against this.** It is a different case:
**181 × 167 × 77 mm** and 2.5 kg, against **400 × 110 × 80 mm** and about 8 kg for one
traction pack. Putting a small 12 V pack on the shelf is not the same as putting two
48 V packs there.

**It is the worst place for a cell to fail.** A box under the frame vents
downwards and away from everything. The same event on the electronics shelf
happens inside the body, next to every board, with the head on top of it.

**It throws away the best volume on the robot.** The box interior is
420 × 244 × 118 mm clear, lower than anything else on the machine, and mass down
there *improves* the tipping instead of hurting it.

### The tipping numbers, for completeness

| | Battery CoM | Robot CoM | Tips forward at |
|---|---|---|---|
| **As built** — packs in the frame | 217 mm | 318.2 mm | **19.3°** |
| If moved to the body shelf | 399 mm | 351 mm | 17.6° |

Moving them up raises the centre of mass 32.7 mm and costs 1.7°. The castor
catches the pitch at 12.3°, so the margin goes from **7.0°** as built to **5.3°**
with the packs in the body, against a guard minimum of 4°.

When this document was first written, that was not a veto on its own and it was
worth saying so. It still is not a veto by itself — but the slack keeps getting
spent by other things. The chest speakers plus the two-floor laptop stack now
leave **6.8°** over the castor, with 6.8 kg of speakers at 613 mm, both forward
of centre. Every heavy thing that moves into the body comes out of the same
margin.

So tipping has gone from "not the reason" to "one of the reasons". The four points
above are still the stronger ones.

> **Do not compare these numbers with an older copy of this document.** They are
> re-read from `cad/walle_frame.scad` on 2026-09-19 and several are different from
> what was written here before, because the model has moved on. Run the model
> rather than trusting any table, including this one.

---

## 3. The one argument for moving them: ground clearance

The plywood box floor is the lowest point of the robot, at 150 mm. Remove the box
and the lowest point becomes the rail bottoms at 197 mm. That is 47 mm of extra
ground clearance, and on rutted sand it is a genuine gain.

If clearance turns out to be the problem, **do not solve it by moving the packs
into the body. Raise the box.** There is unused headroom above it, because the
thing that sets the body floor is the pod belt crown at 327 mm, not the box.

**The limit is 173 mm, which is less than it first looks.** Closing the box cost
some of the headroom: the lid and the foam pad added 20 mm to the top of the box,
and the binding constraint moved. It is no longer the M12 spanner holes — it is
the 20 mm of clearance the lid needs under the body floor, so you can get a
spanner on the lid bolts at all. Checked against the model: at 173 that guard
sits exactly on its minimum, and at 174 it fails.

| | Ground clearance | Robot CoM | Tips forward at |
|---|---|---|---|
| Box floor at 150 (as built) | 150 mm | 318.2 mm | 19.3° |
| Box floor at 173 (the limit) | **173 mm** | 322.4 mm | **19.0°** |
| Packs in the body | 197 mm | 351 mm | 17.6° |

So raising the box buys 23 mm of the 47 for almost nothing — 0.3° — while moving
the packs into the body buys 47 mm for 1.7° and all the heat, access and
failure-mode problems. Owner decision 2026-09-16: leave it at 150 for now and
revisit after the first drive on sand.

Push past 173 and something worse happens than a failed guard. The box top starts
to drive the **body** floor height instead of the belt crown, so the whole robot
grows upward: at a floor of 190 the body rises 13 mm, the centre of mass goes to
361, and you have spent 0.5° of tipping to gain clearance you partly gave back.
If you ever need more than 173, raise it and drop `body_gap` in the same change,
or lie the packs flat to get 30 mm back off the box height.

---

## Summary

The box was open, which was a real fault, and it is now a closed box with a
gasket, plugged spanner holes, a foam pad and a membrane vent in the lid. Daily
charge is through a sealed connector on the body. Every pack still unplugs and
lifts out when you need it (L17).

Keep the packs low. Mostly because they need a sealed case wherever they go, and
once that is true the body is the hottest, most crowded and most dangerous place
to put them — and now partly because of the tipping too, since the chest speakers
have spent most of the margin that used to make the tipping argument optional.

If ground clearance becomes the problem, raise the box floor towards 173 mm.
