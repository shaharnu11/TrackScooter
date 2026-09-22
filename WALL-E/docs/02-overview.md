# 02 — What this robot is

Two-track robot built from the two track pods in `../archive/`. Target: Midburn, Negev desert. The pods are built. This project does not modify them.

- Pods mounted **side by side**, not one behind the other. No steering fork.
- Turning: left track speed ≠ right track speed. Skid steer, as on a digger or a tank.
- On top of the pods: a box holding batteries, three computers, two speakers.
- On the box: a rigid head with two screens as eyes.

![The robot, three quarter view](fig/walle_robot_3q.png)

## Control

- Driven by a person with a radio remote. Teleoperation. **Not self-driving.**
- Two autonomous layers run on top:

| Layer | Function |
|---|---|
| Safety | Sensors detect obstacles. The robot refuses to drive into one, including against driver input. |
| Personality | Camera finds faces. Eyes track them. Whole robot turns to face them, because the head is rigid. Sounds play. |

Rationale: full autonomy in a night-time crowd is higher risk and higher effort, and the crowd does not perceive navigation quality. It does perceive eyes that follow it.

## Three computers

Constraint: the three jobs have incompatible timing requirements. Combining them on one board makes the robot unsafe.

| Name | Board | Job | Timing requirement |
|---|---|---|---|
| **Brain** | Jetson Orin Nano | Camera, AI, sounds, decisions | 0.1–3 s is acceptable |
| **Spine** | Teensy 4.0 | Radio input, motor commands, safety rules | 1 kHz, deterministic |
| **Face** | ESP32-S3 | Two eye screens. No servos | 30 Hz, steady |

- Brain runs Linux: good at large jobs, no timing guarantee. A 2 s stall is acceptable for a camera, not for motors.
- Spine runs no OS. One loop. Cannot stall. Holds the stop rules. Stops the motors if the Brain goes silent.
- Radio receiver and E-stop wire into the **Spine**, not the Brain. A Brain crash costs eyes and sound only; the driver keeps full control.
- Face is separate so eye motion stays smooth while the Brain is loaded. A stuttering eye reads as broken.

## Headline numbers

Body is narrower than the track span by design: the pods stay proud at the sides, which is what makes the silhouette read as WALL-E.

![From the front](fig/walle_robot_front.png)

| Quantity | Value |
|---|---|
| Overall width | 677 mm (pod centres 500 apart) |
| Overall height | 910 mm to the top of the eye barrels |
| Body | 430 long × 620 wide × 400 tall, floor at 335 mm |
| Rails | 60×30×3 box, 550 long, 263 mm clear between |
| Lowest point | 150 mm above ground |
| Mass, whole robot | 88.8 kg — **pods, packs and electronics are estimates** |
| Centre of mass | 318.3 mm up, 4.4 mm forward of centre (chest speakers) |
| Ground pressure | 0.163 kg/cm² over 546 cm² |
| Tips forward at | 19.3° pitch (backward 20.7°) |
| Anti-tip castor catches at | 12.3°, i.e. 7.0° of margin |
| Steel | 1626 mm of 60×30×3 box tube |

Pod removal: 2 bolts per side, 4 total. The frame reuses the M12 holes already drilled in the green plates. The rail lands on the carrier, which stands 6 mm proud of the plate, so each side takes a 6 mm packer under the bolts. Stack detail: part 5.

Tipping figures depend on mass estimates. Weigh a pod and a pack and enter real values before relying on 19.3°.

## Four results from the model

**1. No electronics fit in the frame.** Interior clearances: 8 mm above the packs, 24 mm between them, 13 mm to the cross members. All electronics moved to a shelf in the body: four rows, 40 % of shelf area used, remainder for speakers and airflow.

![The electronics shelf, labelled](fig/walle_shelf.png)

**2. The body floor must clear the belt crown, not the frame.** Belt crown 327 mm, frame top 257 mm. Body sits on four 78 mm risers. Without them the shell contacts a moving belt.

**3. The battery box must be closed.** Previous design: three-sided U, open at top and both ends, positioned where the belts throw sand. Current design: six panels, gasketed lid, plugs in the spanner holes, membrane vent. A sealed box breathes with the day/night temperature cycle and would otherwise draw dust through its worst leak. Packs charge in place through an external connector and do not come out in the field.

![The plywood cutting layout](fig/walle_frame_plates.png)

**4. The chest panel was an opening, not a panel.** `chest_d` recessed the chest 20 mm into a 12 mm wall, removing the front wall entirely and exposing the electronics. Now a 12 mm plate set back 20 mm, which is also the speaker mounting surface.

## Speakers

- 2 × 6.5 inch drivers in the chest panel, 280 mm apart, 584 mm above ground.
- Each driver in its own sealed plywood enclosure, 9.8 litres.
- Sealed, not firing into the body: the body is not airtight (filtered intake, removable lid, cable entries), so an open back loses bass, and 100 W of internal pressure loosens shelf connectors.

![The chest panel and the two sealed enclosures, from behind](fig/walle_chest.png)

Two consequences:

- The enclosures shade 54 % of the electronics shelf, clearing it by 20 mm. They **bolt** to the chest panel. Glued, half the electronics becomes unreachable.
- They cost ~1.5° of forward tipping margin: 7.3 kg at 584 mm, both forward of centre, moving the centre of mass 4.4 mm forward. Result 19.3° with 7.0° of castor margin. Weigh real parts before adding further high or forward mass.

## Head

- 2 barrels, 105 mm, 128 mm apart, toed in 6°.
- Each holds a 2.1 inch round screen, recessed 60 mm behind a clear dome.

![The head, with the two eye barrels](fig/walle_head.png)

The recess is a sun shade, not styling: a screen 60 mm behind a 53 mm aperture is shaded for sun elevation above 49°. Negev midday sun is 75–80°. The dome seals the barrel against dust.

## Current state

- Both pods built. Belts fitted. Both hub motors in hand, with their scooter controllers.
- No electronics built. Frame not welded — first job.

Measured on the built pods, carried by revision rev013:

| Quantity | Value |
|---|---|
| **Carrier outer faces — frame mounting width** | **177 mm** (green plates 165 mm; the 6 mm step is the packer) |
| Ground contact, one pod | 231 mm long × 118 mm wide |
| Pod size | 363 long × 327 tall × 177 wide over the carriers |
| Pod-to-frame band | plate 60 mm tall, 197–257 mm above ground |
| Suspension travel | +30.7 mm, −29.2 mm |
| Ground pressure at 100 kg | 0.18 kg/cm² |
| Belt travel per motor turn | 660 mm |

Source: `../archive/rev013-double-shear/`. Confirm the mounting width with a tape measure before welding.

Ground pressure reference: a human foot is ~0.5 kg/cm². This robot at 100 kg loads the sand at under a third of that. That is the engineering reason for tracks.

## Open questions

Full list with deadlines: part 2, section 4. Three highest priority:

1. **Pack capacities in Ah, and BMS health of both.** Sets runtime and fuse sizing. Since D8 gave the electronics their own battery, the two traction packs should be equal capacity. See D4.
2. **Does the robot carry a person?** If yes: heavier frame, and registration as a mutant vehicle with Midburn. Check current Midburn rules before welding.
3. **Forward tipping.** Track ground contact is 231 mm, which is the entire front-to-back footprint. Longer belts are no longer possible with the pods assembled. Mitigation: anti-tip wheels, and all heavy mass kept low.
