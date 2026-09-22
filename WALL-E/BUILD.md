# Building WALL-E

This is the order to build the robot in, with the check to do at the end of each
step. Every number here comes out of `walle.scad`. None of it is typed in by
hand, so if you change the model, run `./render_all.sh` and this file's drawings
change with it.

Front of the robot is **+x**. When a drawing says "front to the right", that is
what it means.

## The files

| File | What it is |
|---|---|
| `walle.scad` | The global file. One entry point, every view and every sheet. |
| `pod_interface.scad` | The 23 facts about the **built** pods. The only place they live. |
| `check_pod_interface.scad` | Proves that file still matches the real pod model. |
| `cad/walle_frame.scad` | Everything WALL-E decides, plus 46 guards. |
| `render_all.sh` | Regenerates every sheet and every view. |
| `blueprint/s1..s5.png` | The dimensioned drawings. |

To redraw everything:

```sh
cd WALL-E
./render_all.sh
```

It checks the pod numbers and the 46 guards first, and stops if the pod numbers
do not match. That is on purpose: if the pod interface is wrong, every dimension
on every sheet below it is wrong too.

## The sheets

| Sheet | Title | Use it for |
|---|---|---|
| `blueprint/s1.png` | General arrangement | Overall sizes, and every important height |
| `blueprint/s2.png` | Frame weldment | **Give this to the welder** |
| `blueprint/s3.png` | Battery box, 6 panels | **Give this to whoever cuts the plywood** |
| `blueprint/s4.png` | Chest panel / speaker baffle | Cutting the two speaker holes |
| `blueprint/s5.png` | Electronics shelf | Placing the boxes and running the cable |

## The headline numbers

| | |
|---|---|
| Overall | 910 mm tall, 677 mm wide, 430 mm body length |
| Weight | about 100 kg, and **that is a guess** — see step 0 |
| Lowest point | the plywood box floor, 150 mm above the ground |
| Tips forward at | 17.7°, and the castor catches it at 12.3° |
| Speakers | two 6.5 inch, 10.1 litres of sealed air behind each |

---

# Step 0. Before you cut anything

The part weights are still assumptions, and the pod joint is worth a tape
measure. Both are cheap to check now and expensive to discover later.

### 0a. Which face does the rail bolt to? (answered — but look anyway)

This used to be an open question. Rev 013 measured the built pods on
2026-09-18 and closed it:

- The green plates **are** fitted, but they sit **inboard** of the carriers, at
  76.5 to 82.5 mm from the pod centre.
- The carrier is next, 82.5 to 88.5, so it stands **6 mm proud** of the plate.
- The rail therefore **lands on the carrier**, at 88.5. The robot is 677 mm
  wide overall.
- The two M12 holes are in the **green plate**, 6 mm behind that face. Each
  side gets a **6 mm packer** (a 60×6 offcut, 2 holes Ø13) filling the gap.

Without the packer the bolts pull the rail wall into the air gap and the joint
has no clamp at all. Do not skip it.

Go and look at the physical pods anyway, and check the table in step 0a2. The
scooter's fork legs, if they are still bolted on at 88.5 to 92.5, come **off**
for WALL-E — they belong to the scooter.

Full stack, part by part: [FRAME_AND_PODS.md](FRAME_AND_PODS.md).

### 0a2. Measure the gap between the fork legs before you cut anything

**Do this one with a tape measure, not by trusting this document.**

On 2026-09-17 the checker found that the WALL-E frame had been built on
`fork_gap = 168` when the real Rev 012 value is **140**. The 168 came from a
proposal to widen the carrier spacing that was then reverted, so it had never
been true. The frame was **14 mm per side too wide**, and the drawings said
700 mm overall when the answer is 672.

It is fixed now. But it is exactly the kind of error that survives right up to
the moment the steel is already cut, so verify it yourself:

| Measure | Should be |
|---|---|
| Clear gap between the two carrier plates | 165 mm |
| Over the carriers, outer face to outer face | 177 mm |
| Over the two green plates | 165 mm |
| Carrier plate thickness | 6 mm |
| Green plate thickness | 6 mm |
| Green plate band, bottom and top above ground | 197 and 257 mm |
| M12 hole centres, forward of the hub axle | 108 and 168 mm |

If any of these differ, change them in `pod_interface.scad`, then run:

```
cd WALL-E
./pod_latest.sh
openscad -o chk.echo --export-format echo check_pod_interface.scad
./render_all.sh
```

The checker tells you whether the numbers still match the pod model, and the
render script re-cuts every drawing. Never edit a dimension in `walle_frame.scad`
to work around a pod measurement.

### 0b. Weigh things

The tipping angles are the only thing keeping the robot off its face, and they
are computed from these guesses:

```
pod 15 kg each · battery 8 kg each · electronics 6 kg · body 25 kg · head 5 kg
```

Put a pod on a bathroom scale. Weigh a battery pack. Then open
`cad/walle_frame.scad`, find the block marked `STILL GUESSES`, replace the
numbers, and re-run. If the forward tipping angle drops below about 15°, stop
and move weight backwards before you build the body.

**Check:** `./render_all.sh` prints `all 46 guards pass` and
`ALL 23 NUMBERS AGREE`.

---

# Step 1. Cut the steel

From sheet 2. All of it is 60x30x3 box tube except the castor legs.

| Part | Count | Length |
|---|---|---|
| Rail | 2 | 550 mm |
| Cross member | 2 | 240 mm |
| Castor leg, 30x30 box | 2 | 87 mm |
| Castor fore/aft tie | 2 | — |

That is 1580 mm of 60x30 box in total.

**Check:** both rails are the same length to within 1 mm. If they are not, the
bay will not be square and the pods will toe in or out.

---

# Step 2. Drill the rails

This is the step to get right, because the holes in the pods already exist and
cannot move.

Each rail gets **2 holes Ø25, straight through both walls**:

- at **107 mm and 167 mm from the rail's REAR end**
- **30 mm up from the rail's bottom edge**

Then **weld a Ø25 / Ø13 x 30 mm sleeve into each hole.** The sleeve is what
carries the load across both walls of the box section. Without it you are
crushing a 3 mm wall with an M12 bolt.

> The rear end is the **−x** end. This file used to say "front end" and the
> distances were being measured from the rear, which would have put both holes
> 336 mm out of place. Measure from the rear.

**Check:** hold a rail against a pod, flat on the **carrier** face, with the
6 mm packer between the rail and the green plate. The two sleeves should line up
with the two drilled holes in the plate with no forcing. Do this before you weld
anything else.

---

# Step 3. Weld the frame

From sheet 2, plan view. Distances are from the rail's rear end.

- Rail outer faces **323 mm apart**, so **263 mm clear** between them.
- Rear cross member at **25 mm**.
- Front cross member at **525 mm**.
- Both cross members sit **between** the rails, so cut them to the bay: **263 mm**.

The rails end up sitting **197 to 257 mm above the ground**, which is flush with
the green plates.

Then the anti-tip legs: two 87 mm uprights with Ø75 castors, 280 mm out from the
centre, set so the castor wheel is **35 mm clear of the ground**.

**Check:** measure both diagonals across the bay. They must match. Then check
the clear bay is 268 mm at both ends, not just in the middle.

---

# Step 4. Bolt the frame to the pods

Four M12 10.9 bolts, two per side, through the rail into the nut on the green
plate.

Tighten to a normal M12 10.9 torque. Each bolt only sees about 1.2 kN of the
50 kN of preload available, so the joint is nowhere near its limit — the margin
is in the plates, not the bolts.

**Check:** stand back and look at it from the front. Both pods should be
vertical and the frame level. Then push the robot. **The whole pod comes off
with two bolts per side** — that is the point of this joint, so make sure you
can still reach all four heads.

---

# Step 5. The battery box

From sheet 3. Six panels of 12 mm plywood, cut from one sheet.

| Panel | Count | Size |
|---|---|---|
| Floor | 1 | 444 x 240 |
| Side wall | 2 | 444 x 142 |
| End wall | 2 | 240 x 142 |
| Lid | 1 | 444 x 240 |

The side walls are **handed**. Each one gets two **Ø30 holes at 54 mm and
114 mm from the rear edge, 77 mm up**. Those are spanner access for the M12 pod
bolts, not ventilation.

The lid gets **12 x M5 round the edge at 110 mm pitch**, and **one Ø12 screw-in
membrane vent in the centre**, sitting over the gap between the two packs.

Assembly order:

1. Floor and four walls. The end walls are what actually close the box.
2. **3 mm closed-cell foam tape on every face the lid touches.**
3. Batteries in, standing upright: 80 mm wide, 110 mm tall.
4. **8 mm foam pad on top of the packs**, so the lid holds them down.
5. Lid on, 12 x M5.
6. **4 x Ø30 silicone blanking plugs** into the spanner holes.

The plugs go in **after** the pod bolts are torqued. If you seal them first you
will be cutting them out again.

### Charge the packs where they are

The box is sealed and there is no field-serviceable way into it. Run the charge
leads out through a gland and charge in place. Do not plan on lifting packs out
in sand.

**Check:** the box floor is **150 mm above the ground and is the lowest part of
the whole robot.** Everything you drive over has to clear that, not the tracks.

---

# Step 6. The body and the chest panel

The body floor sits at **335 mm**, which is 8 mm over the pod belt crown. The
crown is higher than anything at frame level, so it is the crown that sets this
height, not the frame.

Body is **430 long x 620 wide x 400 tall**, on 78 mm risers off the rail tops.

The chest panel, from sheet 4:

- 12 mm plywood, **510 x 290**
- **set back 20 mm** from the body's front face
- **two Ø165 holes**, centres **280 mm apart**, **194 mm up from the panel's
  bottom edge**

The Ø190 driver rim lands on the panel face around each hole, with 20 mm of
margin left and right and 50 mm top and bottom.

**Check:** dry-fit a driver in each hole before you glue the panel in. The rims
must not touch each other — there should be 90 mm between them.

---

# Step 7. The speaker enclosures

One sealed box per driver, **260 deep x 258 tall x 205 wide** in 12 mm ply. That
gives **10.1 litres of air** behind each driver, which is in the middle of the
7 to 14 litre range a 6.5 inch driver wants.

**Bolt them to the chest panel. Do not glue them in.** Each one sits over the
electronics shelf with 20 mm of headroom and covers 54% of it. With both boxes
in place only **46% of the shelf is reachable**, so if they are glued you cannot
service the electronics without destroying something.

Seal every joint. A sealed box that leaks is an unsealed box, and it will chuff
and rattle at volume.

Fit the metal grilles.

**Check:** press a cone in gently with your palm. It should feel springy and
push back. If it moves freely, the box is leaking.

---

# Step 8. The electronics shelf

From sheet 5. The shelf is **356 x 546 at 347 mm**, four rows running fore and
aft. The parts use 32% of the area and the tallest box is 76 mm.

Mount everything **before** the speaker enclosures go in, and leave the cable
long enough that a box can be lifted out without unplugging the whole robot.

See `docs/04-power-and-wiring.md` for the wiring. The one thing worth repeating
here: the **amplifier gets its own 48 V to 32 V supply**, separate from the
logic supply. Sharing it puts motor noise straight into the speakers.

**Check:** with both enclosures bolted in, can you still reach every connector
you might need on a bad day at the festival? If not, move it now.

---

# Step 9. The head

**The neck is a rigid welded post. It is not a joint.** No bearing, no slip ring,
nothing to rotate and nothing to seal. The head does not pan, nod, or tilt.
To look left or right, the whole robot turns.

Neck 70 mm tall off the body top at 735 mm. Head centre at 858 mm, 233 mm wide,
two Ø105 barrels 128 mm apart. **Robot height 910 mm.**

Each eye is a 53 mm screen sunk **60 mm** into its barrel. That fills 50% of the
barrel and shades the screen from any sun above **49° elevation**. Negev midday
sun is 75 to 80°, so the screens are shaded when it matters.

**Check:** the barrels toe inwards. Check the two mouths clear each other —
there should be 7 mm between them. Rotate them through their full travel.

---

# Step 10. Before you drive it

1. Put it on level ground. Both castors should be **35 mm clear**.
2. Push down hard on the front. The castor must touch **before** the robot
   starts to go over. It catches at 12.3° and the robot goes over at 17.7°, so
   there is 5.4° in hand.
3. Drive it slowly on sand. Ground pressure is 0.184 kg/cm², about a third of
   what a walking person puts down, so it should float.
4. Watch the **box floor at 150 mm**, not the tracks. That is what grounds out.

---

# When you change something

```sh
cd WALL-E
./render_all.sh
```

Read the output. `all 46 guards pass` and `ALL 23 NUMBERS AGREE` means the
change is consistent. A `WARN` line names the clearance that has gone negative
and by how much. A `MISMATCH` means `pod_interface.scad` no longer agrees with
the pod model, and nothing below it can be trusted until that is fixed.
