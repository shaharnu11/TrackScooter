# 02 — The lower shock bolt warning, explained

The pod model prints two warnings every time it runs. They have been there since Rev 011, and
both pods were built with the condition they describe. This document explains exactly what
they mean, how serious they are, and what to do about it now that the pods are assembled.

The two lines, exactly as the model prints them:

```
*** WARN lower shock bolt bending, trailing arm: lever 41 mm, 2681 N at full bump
    -> 351 MPa — over mild-steel sleeve yield (235) before any impact. Support the
    eye's OUTER end (double shear: clevis / outer strap), or a much stiffer pin.

*** WARN lower shock bolt bending, leading arm: lever 33 mm, 2681 N at full bump
    -> 284 MPa — over mild-steel sleeve yield (235) before any impact. Support the
    eye's OUTER end (double shear: clevis / outer strap), or a much stiffer pin.
```

---

## 1. Which part this is about

Each arm carries one shock absorber. The shock's **lower eye** is the ring at its bottom end.
That ring sits on a spacer sleeve, Ø15 mm on the outside and Ø9 mm through the middle, and an
M8 bolt runs through the sleeve to hold the whole thing to the arm.

The problem is how that bolt is held. It passes through the arm's plate on the **inboard**
side, and then sticks out towards the outside of the pod. The shock eye sits near the far end.
**Nothing holds that far end.** It hangs in the air.

```
  inboard                                                    outboard
     |
     |  arm plate            spacer sleeve          shock eye
     |  ██████ ═══════════════════════════════════  ████
     |  ██████                                      ████   <-- force from
     |    ^                                          ^          the spring
     |    |                                          |          acts HERE
     |  held here                              nothing holds
     |  (one side only)                        this end
```

An engineer calls this **single shear**, or a **cantilever**. A diving board is the everyday
version: fixed at one end, loaded at the other, and it bends.

---

## 2. Why it bends, and how much

Three numbers decide it.

### The force: 2681 N

The springs are rated "100 kg / 8.5 mm", which works out to 115 N of force for every
millimetre you compress them. The shocks are 150 mm from eye to eye when free, with 30 mm of
stroke.

| Suspension position | Spring force per shock |
|---|---|
| Hanging free, full droop | −318 N (the spring is pushing the arm down) |
| Sitting at ride height | 1150 N |
| **Full bump, arm all the way up** | **2681 N** |

2681 N is about 273 kg of force. That is the load pushing sideways on the end of that bolt
when the suspension is fully compressed.

### The lever: 41 mm and 33 mm

This is the distance from the supported point to where the force acts — the length of the
diving board.

The two arms are different because they sit at different depths in the pod:

| | Arm plate outer face | Shock eye centre | Lever |
|---|---|---|---|
| Trailing arm | 31.75 mm | 73 mm | **41.25 mm** |
| Leading arm | 39.60 mm | 73 mm | **33.40 mm** |

(All measured from the pod's centre plane. The trailing arm sits further inboard, so its bolt
has to reach further out, so its lever is longer and it is the worse of the two.)

### The section: 315 mm³

How much the part resists bending. Engineers call it the **section modulus**, written Z.
Bigger is stiffer. It is worked out from the sleeve's tube shape plus the bolt inside it:

```
Z = π(15⁴ − 9⁴)/(32 × 15)    the Ø15/Ø9 sleeve      = 288.4 mm³
  + π(6.47³)/32               the M8 bolt's core     =  26.6 mm³
                                                       ─────────
                                                       315.0 mm³
```

The important thing about Z is that it grows with the **cube** of the diameter. Making a pin
slightly fatter helps a great deal; making it slightly thinner hurts a great deal.

### Putting them together

Bending stress is force × lever ÷ Z:

```
Trailing arm:  2681 N × 41.25 mm ÷ 315 mm³ = 351 MPa
Leading arm:   2681 N × 33.40 mm ÷ 315 mm³ = 284 MPa
```

---

## 3. Why 235 MPa is the line

Mild steel — ordinary, unhardened, general purpose steel — bends permanently once the stress
inside it passes about **235 MPa**. That point is called the **yield strength**.

Below yield, steel behaves like a very stiff spring: it flexes and springs back exactly. Above
yield it stays bent. Nothing dramatic happens at the moment you cross the line; the part just
does not come back.

So:

| Position | Stress in the trailing arm's bolt | Verdict |
|---|---|---|
| Ride height, standing still | 151 MPa | Safe, with margin |
| **Full bump** | **351 MPa** | **1.5× past yield** |

The leading arm is 284 MPa, which is 1.2× past yield. Both are over.

---

## 4. The phrase that matters most: "before any impact"

The 2681 N figure is the **static** spring force — what you get by slowly compressing the
suspension to its limit and holding it there.

Real driving does not do that. Driving off a kerb, dropping into a rut, or hitting a rock
compresses the suspension **fast**, and a fast load is much larger than the slow one. How much
larger depends on the speed and the drop, but a factor of two or three is ordinary for a
vehicle suspension.

So the warning is saying: *this part is already past its limit under the gentlest possible
version of the load, before we even start talking about real impacts.*

---

## 5. What would actually happen

Not a sudden snap. Mild steel is well behaved and bends first. The sequence would be:

1. **First hard hit.** The sleeve and bolt take a permanent bend, perhaps a millimetre or two
   at the tip. You would probably not notice.
2. **The shock stops working straight.** Its lower eye is no longer square to the arm, so the
   shock is being worked sideways as well as along its axis. It starts to bind, and its
   damping and travel get worse.
3. **Each later hit bends it more,** and the increasing angle makes each hit worse than the
   last. It gets worse in an accelerating way, not a steady one.
4. **Fatigue.** Metal that is repeatedly bent past yield eventually cracks, even at loads it
   survived the first time. The crack starts where the stress is highest, right at the arm
   plate's outer face.
5. **Fracture.** The bolt breaks and the shock comes off the arm. That arm now has no spring
   at all, so that side of the pod drops onto the belt. If it happens while driving, the robot
   lurches to one side.

That last step is the one that matters for a machine operating near people. It is unlikely to
happen quickly, and it is very unlikely to happen at the low speeds this robot will do. But it
is a known, calculated, avoidable weakness, and it is cheap to fix.

---

## 6. How to check your own pods

Look at the bottom end of one shock, from the outside of the pod.

**Ask one question: is there metal on both sides of the shock's lower eye, or only on the
inboard side?**

- **Metal on the inboard side only**, with the eye's outer face open to the air — this is
  single shear, and both warnings apply to your pods. This is what the drawings specify, so
  it is what you should expect to find.
- **Metal on both sides**, with the eye sitting in a U-shaped bracket or between two plates —
  this is double shear, the problem is already solved, and you can ignore this document.

Check both arms on both pods. There are four in total, and the trailing arm is the worse one.

---

## 7. How to fix it

The warning offers three routes. On a pod that is already built, they are not equally
practical.

### Option A — A much stronger sleeve. Recommended.

**Change the material, not the geometry.**

The warning compares 351 MPa against 235 MPa, the yield strength of *mild* steel. That number
is a property of the material, not of the shape. Higher grade steels are far stronger:

| Sleeve material | Yield strength | Safety factor at 351 MPa |
|---|---|---|
| Mild steel (what is fitted now) | 235 MPa | **0.7 — it yields** |
| Grade 8.8 alloy steel | 640 MPa | 1.8 |
| Grade 10.9 alloy steel | 940 MPa | 2.7 |
| Hardened ground dowel pin | 1200 MPa and up | 3.4 and up |

So: make a new Ø15 outside, Ø9 inside sleeve from grade 10.9 or better, fit it in place of the
mild steel one, and use a grade 10.9 M8 bolt through it. **Every dimension stays exactly the
same.** The geometry, the shock position, the suspension behaviour, and all the clearance
checks in the model are untouched.

Why this is the right choice here:

- It needs no change to the arms, which are welded and finished.
- It costs a few tens of dollars and an hour per pod.
- A safety factor of 2.7 covers the impact loads that section 4 warns about.
- It cannot introduce a new clearance problem, because nothing moves.

Practical ways to get the sleeve: buy a hardened dowel pin and have the Ø9 bore drilled, cut
it from 4140 or similar bar, or cut a length from the shank of a grade 10.9 bolt and drill it
through. Any machine shop will do this in minutes. Ask for four, plus spares.

### Option B — Support the outer end. The textbook answer, but hard now.

Add a plate outboard of the shock eye so the bolt is held at both ends. The bending lever then
almost disappears, and the load becomes pure shear, which a bolt handles very well. This is
what you would design in from the start.

**The problem is space.** Working from the model's numbers, the eye's outer face sits at about
85.5 mm from the pod centre, and the carrier plate's inner face is at 88 mm. That leaves
roughly **2.5 mm** — not enough for a useful plate.

Before ruling it out, measure the real thing: the width of the shock's lower eye, and the
actual clear gap between the eye's outer face and the carrier plate. If there is more room
than the model suggests, this becomes attractive again. If there is 2.5 mm, it is out.

### Option C — A fatter pin. Does not work here.

Section modulus grows with diameter cubed, so a fatter pin helps quickly. To get 351 MPa down
under 235 you need Z above about 470 mm³, which means a solid pin of roughly Ø17.

But the shock eye is bored Ø15 to fit the current sleeve. A Ø17 pin does not go in without
re-boring the eye, which weakens the eye and is not something to do to a bought shock.

**Option C is only worth considering combined with Option A**, and Option A alone already
solves it.

---

## 8. Decision and next step

This is decision **D2** in `00-plan.md`.

Recommended: **Option A**, a grade 10.9 or hardened sleeve, four of them plus spares.

Order of work:

1. Inspect all four lower shock mounts, per section 6, and confirm they are single shear.
2. Measure the shock eye width and the clear gap out to the carrier plate. Write both numbers
   in this file. If the gap turns out to be 8 mm or more, reconsider Option B.
3. Have four sleeves made in grade 10.9 or better, Ø15 outside, Ø9 inside, the same length as
   the ones fitted — the model says about 28.4 mm, but measure the real one.
4. Fit them with grade 10.9 M8 bolts and new nyloc nuts.
5. Update the model so the warning reflects the new material, and note the change in
   `FASTENERS.md` in the pod archive.

Until step 4 is done, do not load the pods with the full robot weight and do not drive over
anything that fully compresses the suspension.

### Measurements to fill in

| What | Model says | Measured | Date |
|---|---|---|---|
| Shock lower eye width | ~25 mm (inferred) | | |
| Eye outer face to carrier plate, clear gap | ~2.5 mm | | |
| Spacer sleeve length | 28.4 mm | | |
| Sleeve outside diameter | 15 mm | | |
| Sleeve bore | 9 mm | | |
| Single or double shear? | single | | |
