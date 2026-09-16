# 06 — Why the batteries are low, and not in the body

A reasonable question, asked on 2026-09-16. The body has plenty of spare room on
the electronics shelf, and putting the packs there would mean no plywood box
slung under the frame at all. So why hang them below?

Run `cad/walle_frame.scad` and it prints the comparison. This document is the
reasoning behind those numbers.

---

## The numbers

| | Battery CoM | Robot CoM | Tips forward at |
|---|---|---|---|
| **As built** — packs in the frame | 217 mm | 332 mm | **19.2°** |
| If moved to the body shelf | 399 mm | 364 mm | 17.6° |

So moving them up raises the robot's centre of mass by 32 mm and costs 1.6° of
tipping margin.

**That on its own is not a veto, and it is worth being honest about that.** The
anti-tip castor catches the pitch at 12.3°, so the margin would go from 6.9° to
5.3°, which still passes the model's check. Tipping is not the reason.

---

## The four reasons that are

### 1. The shelf cannot really take them

A pack is 400 mm long and the shelf is only 356 mm deep, so the packs **cannot
lie fore-aft at all.** They would have to lie across the robot, and then the two
of them use 50 % of the shelf area on top of the 32 % the electronics already
need. That is 83 % of the shelf gone.

What is left has to hold two 6.5 inch speakers and a clear air path past the
Jetson and the two VESCs. It will not.

### 2. The body is the hottest place on the robot

Inside the body there is a Jetson putting out 25 W, two VESCs, and an amplifier,
in a sealed foam-lined box, in the Negev in summer.

Lithium cells lose life quickly above 45 °C, and that is the normal degradation
case, not the failure case. Down in the frame the packs sit in open air
underneath the body, in the draught of driving. That is the single best-cooled
location on the whole machine, and it costs nothing to use it.

### 3. If a pack does fail, where it fails matters

An open-bottomed plywood tray under the frame lets a venting cell dump downwards
and away from everything. The same event on the electronics shelf happens inside
a closed foam box, next to every board on the robot, with WALL-E's head on top of
it.

### 4. It throws away the best space on the robot

The frame interior is 444 × 240 × 110 mm of volume, lower than anything else, and
mass down there is free — it improves the tipping instead of hurting it. Filling
it with air and then carrying 16 kg at shelf height is the wrong way round.

There is also a practical cost: charging means lifting two 8 kg packs up over a
400 mm body wall and down onto a shelf, every day, in the dark, in dust. Out of a
tray at knee height it is a two-second job.

---

## The one real argument the other way

The plywood box floor is the lowest point of the robot, at 150 mm. Take the box
away and the lowest point becomes the rail bottoms at 197 mm. **That is 47 mm of
extra ground clearance, and on soft sand with ruts it is a genuine gain.**

If clearance turns out to be the problem, do **not** solve it by moving the packs
into the body. Solve it by raising the box.

### Raising the box instead

The pack top is currently at 272 mm and the thing above it — the pod belt crown —
is at 327 mm. So there are 55 mm of unused headroom. The box can simply move up.

The limit is not the crown. It is the M12 bolt access holes in the box side
walls, which have to stay clear of the floor. That caps the floor at 190 mm:

| | Ground clearance | Battery CoM | Robot CoM | Tips forward at |
|---|---|---|---|---|
| Box floor at 150 (as built) | 150 mm | 217 mm | 332 mm | 19.2° |
| Box floor at 190 (the limit) | **190 mm** | 257 mm | 339 mm | **18.8°** |
| Packs in the body | 197 mm | 399 mm | 364 mm | 17.6° |

Raising the box buys almost all of the clearance for a quarter of the tipping
cost, and none of the heat, access or failure-mode problems.

One consequence to design for: with the floor at 190 the side walls are only
60 mm tall, so the 110 mm packs stand mostly above the walls. The box becomes a
shallow tray, and the packs then need a strap or a lid across the top to hold
them down rather than relying on the walls.

---

## Summary

Keep the batteries low. Not because of the tipping, which is affordable, but
because the body has no room for them, it is the hottest and most enclosed place
on the robot, it is the worst place for a cell to fail, and it wastes the one
volume where mass is actually helpful.

If ground clearance becomes the problem, raise the box floor towards 190 mm.
