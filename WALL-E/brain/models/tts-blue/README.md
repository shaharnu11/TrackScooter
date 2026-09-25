# ONNX export — text2latent_v2_ru @ step 748000

Multilingual 44.1 kHz TTS exported from `checkpoints/text2latent_v2_ru/ckpt_step_748000.pt`.
Languages in the training mix: **he, en, de, it, es, ru, yi**.

Every checkpoint hash this was built from is recorded in `manifest.json`. A text2latent
checkpoint is only valid against the stats file it was normalized with, so `stats.npz`
here (from `stats_yiddish.pt`) is part of the export, not an interchangeable artifact.

## Contents

| file | what |
| --- | --- |
| `reference_encoder.onnx` | reference latents → 50 style tokens |
| `text_encoder.onnx` | phoneme ids + style → text embedding |
| `vector_estimator.onnx` | flow-matching velocity net (the sampler's inner loop) |
| `vocoder.onnx` | latents → waveform |
| `duration_predictor.onnx` | total duration, from reference latents |
| `duration_predictor_style.onnx` | total duration, from precomputed style tokens |
| `stats.npz` | `mean`, `std`, `normalizer_scale` for latent normalization |
| `uncond.npz` | `u_text`, `u_ref` — the CFG unconditional embeddings |
| `vocab.json` | IPA symbol → id (256-token universal vocab, PAD=0/BOS=1/EOS=2) |
| `tts.json` | copy of `configs/tts.json`, the architecture source of truth |
| `manifest.json` | source checkpoints + sha256 of every file here |
| `voices/*.json` | precomputed speaker styles (see below) |

## Graph signatures

Batch is fixed at **1**; only the time axes are dynamic.

```
reference_encoder       z_ref[1,144,T_ref] mask[1,1,T_ref]              -> ref_values[1,50,256]
text_encoder            text_ids[1,T_txt] style_ttl[1,50,256]
                        text_mask[1,1,T_txt]                            -> text_emb[1,256,T_txt]
vector_estimator        noisy_latent[1,144,T_lat] text_emb[1,256,T_txt]
                        style_ttl[1,50,256] latent_mask[1,1,T_lat]
                        text_mask[1,1,T_txt] current_step[1]
                        total_step[1]                                   -> denoised_latent[1,144,T_lat]
vocoder                 latent[1,24,T_dec]                              -> waveform[1,T_wav]
duration_predictor      text_ids[1,T_txt] z_ref[1,144,T_ref]
                        text_mask[1,1,T_txt] ref_mask[1,1,T_ref]        -> duration[1]  (linear seconds)
duration_predictor_sty  text_ids[1,T_txt] style_dp[1,8,16]
                        text_mask[1,1,T_txt]                            -> duration[1]  (linear seconds)
```

Two things that are easy to get wrong:

* **`vector_estimator` bakes in the Euler step.** It returns `x + (1/total_step) * v`, not
  the velocity. Classifier-free guidance has to blend velocities, so recover
  `v = (out - noisy_latent) * total_step` before mixing cond/uncond.
* **The latent axes are the compressed ones.** The VF and DP work on `[1, 144, T]` at
  14.35 Hz; the vocoder wants `[1, 24, 6T]`. Fold with
  `z.reshape(1,24,6,T).transpose(0,1,3,2).reshape(1,24,6T)`, and denormalize first:
  `z = (x / normalizer_scale) * std + mean`.

## Voices

Precomputed styles, so synthesis never needs a reference wav or the AE encoder.
Schema matches what the repo already reads (`inference_tts.py --style_json`,
`benchmark_trt.load_style_json`, `inference_helper.load_voice_style`):
`style_ttl [1,50,256]` for the acoustic model, `style_dp [1,8,16]` for
`duration_predictor_style.onnx`.

| voice | reader | F0 | source |
| --- | --- | --- | --- |
| `libri_male_6209` | 6209 deckerteach | 128 Hz | LibriTTS-R train-clean-100 |
| `libri_male_8088` | 8088 Jason Bolestridge | 112 Hz | LibriTTS-R train-clean-100 |
| `libri_female_6147` | 6147 Liberty Stump | 211 Hz | LibriTTS-R train-clean-100 |
| `libri_female_1088` | 1088 Christabel | 204 Hz | LibriTTS-R train-clean-100 |
| `female` | — | 180 Hz | in-house `female1_hebrew_slow` — **check rights before shipping** |

LibriTTS-R is CC BY 4.0 (Google LLC). Those references are 24 kHz upsampled to 44.1 kHz,
so they carry no content above 12 kHz — the same form the model saw in training.

Add one with:

```bash
python scripts/make_onnx_voice.py --onnx_dir onnx_models_ru_748000 \
    --name <name> --ref_wav <wav>
```

## Running

```bash
python scripts/run_onnx_inference.py --onnx_dir onnx_models_ru_748000 \
    --voice libri_male_6209 --ipa_json <ipa.json> --steps 16 --cfg 3.0
```

Input is **IPA**, not raw text — phonemization stays outside the export, because each
language has its own front end (Phonikud for he, nikud + `yiddish_g2p` for yi, RUAccent +
RUPhon for ru, espeak for the rest). `--ref_wav` is also accepted, but encoding a wav to
latents needs the PyTorch AE encoder: `export_onnx.py` exports the decoder only.

Verified against the PyTorch path from identical initial noise: waveform cos-similarity
≥ 0.9995 in all 7 languages, duration agreeing to ~1e-6 s.

## Russian front end (`g2p/russian_g2p.py`)

Bundled here because it is the front end this checkpoint was trained with — feed it
anything else and the stress/reduction pattern will not match what the model saw.

```
Cyrillic --RUAccent--> '+'-accented --RUPhon--> IPA --remap--> vocab.json symbols
```

1. **RUAccent** resolves lexical stress from sentence context and restores omitted ё
   (~34% of `russian_librispeech` rows need it; ё is always stressed).
2. **RUPhon** applies stress-conditioned vowel reduction — the thing that makes Russian
   sound Russian: `зам+ок → zɐmˈok` vs `з+амок → zˈamək`.
3. **`remap_ruphon_ipa`** folds RUPhon's tilde tie-bars (`t~s`, `t~ɕ`, …) onto the single
   ligatures in `vocab.json` (`ʦ`, `ʧ`, `ʣ`, `ʤ`) and converts the ASCII stress mark `'`
   to IPA `ˈ` (U+02C8). Without this last step stress silently trains into the
   *apostrophe* embedding — in-vocab, so it never raises an OOV.

```python
from g2p.russian_g2p import phonemize_russian, remap_ruphon_ipa

phonemize_russian("на горе стоит замок")   # raw Cyrillic -> vocab-ready IPA
remap_ruphon_ipa("zɐm'ok t~sar")           # -> "zɐmˈok ʦar"  (stage 3 alone)
```

`phonemize_russian` / `accent_russian` need `pip install ruaccent ruphon 'transformers<5'`.
That pin is why the two stages are kept out of the training env — phonemize offline into
an `ipa` column. `remap_ruphon_ipa`, `mark_yo_stress` and `apply_word_overrides` are pure
string work and safe to import anywhere.

Two deliberate quirks: `ч /tɕ/` and `тш /tʂ/` both map to `ʧ`, sharing an embedding with
the English/Yiddish affricate rather than getting a symbol of their own; and `всё` carries
a hard IPA override, because RUPhon reads it as `fsʲe` — which is the *correct* reading of
`все` ("all"), so no respelling can fix it and the substitution has to know the source word.

**Not espeak-ng:** its `ru` voice is context-invariant (`висит замок` and `стоит замок`
phonemize identically), cannot restore written-out ё, and emits `ы` as `/y/`, colliding
with the German ü already in this vocab.

## Known issues

* **Output can exceed ±1.0** (up to 1.5 measured on loud references) — anything writing
  PCM_16 must peak-limit or it clips silently. `run_onnx_inference.py` limits to 0.95.
* **Italian under-predicts duration by ~36%**, well outside the 0.74–1.02 band of the
  other languages, so it sounds rushed. `--speed 0.7` compensates.
* **Duration saturates near ~16.5 s.** Longer text has to be synthesized per sentence and
  joined; see the `--chunk` note in `scripts/run_ipa_inference.py`.
* **Unknown IPA symbols map to PAD and vanish** without raising. Check coverage against
  `vocab.json` when adding a language.
