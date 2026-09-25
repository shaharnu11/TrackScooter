# 02 — What this robot is

Two-track robot on the pods in `../archive/`. Midburn, Negev. Pods are built. This project does not modify them.

- Pods **side by side**. Skid steer. No steering fork.
- Box on top: batteries, three computers, two speakers.
- Rigid head. Two screens as eyes.

![The robot, three quarter view](fig/walle_robot_3q.png)

## Control

- A person drives with a radio. **Not self-driving.**
- Safety: sensors veto obstacles, including against the stick.
- Personality: camera finds faces, eyes follow, body turns (head is rigid), sounds play.

## Three computers

| Name | Board | Job | Timing |
|---|---|---|---|
| Brain | XPS 15 9510 (owned) | Camera, local LLM, sounds | 0.1–3 s OK |
| Spine | Teensy 4.0 | Radio, motors, stop rules | 1 kHz |
| Face | ESP32-S3 × 2 | Two eye screens. No servos | 30 Hz |

- No internet. Radio and E-stop into the Spine.
- Brain crash: eyes and sound die. Driver keeps control.

## Numbers

Body narrower than the tracks on purpose.

![From the front](fig/walle_robot_front.png)

| | |
|---|---|
| Width | 677 mm (pod centres 500) |
| Height | 910 mm to barrel tops |
| Body | 430 × 640 × 400, floor 335 mm |
| Rails | 60×30×3, 550 long, 263 mm clear |
| Lowest point | 150 mm (box floor) |
| Mass | 91.6 kg — pods/packs/electronics still guesses |
| CoM | 323.5 mm up, 3.9 mm forward |
| Tips forward | 19.0° (back 20.3°) |
| Castor catches | 12.3° — **6.8°** margin |
| Ground pressure | 0.168 kg/cm² |

Pod off: 2 × M12 per side. Rail on the carrier. 6 mm packer. Weigh a pod and a pack before trusting 19.0°.

## Model results

1. **No electronics in the frame.** 8 mm above packs, 24 mm between. Two floors in the body. 12 V pack 181 × 167 × 77 mm on the lower deck (not the 400 × 110 × 80 mm traction case). Upper: 315 × 360 mm tray for closed XPS + USB hub. Speaker boxes off, then tray out.

![The electronics shelf, labelled](fig/walle_shelf.png)

2. **Body floor clears the belt crown** (327 mm), not the frame (257 mm). Four 78 mm risers.

3. **Battery box closed.** Six panels, gasket, plugs, vent. Daily charge in place. Packs still lift out (L17).

![The plywood cutting layout](fig/walle_frame_plates.png)

4. **Chest is a 12 mm plate**, set back 20 mm. Speaker baffle.

## Speakers

- 2 × 6.5 inch, 330 mm apart, 613 mm up. On the chest edges. 140 mm between rims.
- 7 inch LCD, 107 × 183 mm, **portrait**, between them. HDMI from the XPS. Glass window 90 × 160. Bezel on the chest, not through the speaker boxes.
- 7.5 L sealed box each. Bolt on. Shade 54 % of the shelf.
- 6.8 kg, both forward. Same 6.8° castor margin. Weigh before adding high/forward mass.

![The chest panel and the two sealed enclosures, from behind](fig/walle_chest.png)

## Head

- Barrels Ø105, 128 mm apart, toe 6°.
- 2.1 inch screens, 60 mm recess, clear dome. Shade above 49° sun. Midday 75–80°.

![The head, with the two eye barrels](fig/walle_head.png)

Camera under the brow: ELP cube 42 × 42 × 36 mm, 86°.

## Built pods (rev013)

| | |
|---|---|
| Mounting width | **177 mm** over carriers (plates 165 mm) |
| Contact | 231 × 118 mm |
| Pod | 363 × 327 × 177 mm |
| Band | 60 mm, 197–257 mm up |
| Travel | +30.7 / −29.2 mm |

`../archive/rev013-double-shear/`. Tape-measure before welding.

## Open

1. D4 — pack Ah and BMS. Equal traction packs.
2. D3 — carry a person? Midburn rules before weld.
3. D6 — anti-tip. 231 mm is the whole footprint.
