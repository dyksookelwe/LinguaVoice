# Experiments

## Voice Cloning

### Goal

Find a voice cloning solution that preserves speaker identity when generating Slovak speech from a short English voice reference.

### Preliminary results

| Provider | Test | Observation |
|---|---|---|
| ElevenLabs Instant | Short and ~2-minute references; English and Slovak output | Longer reference improved similarity, but the generated voice was still noticeably different. Changing the output language made little difference. |
| Cartesia | English and Slovak output | More convincing similarity, but listeners did not consider it the same voice. |
| Polyvox | Short reference; Slovak output | Best result among tested providers. Listeners noticed similarities, but the voice was still not reliably perceived as the same person. |

**Current conclusion:** Polyvox is the leading candidate, not a final choice. These results are preliminary and based on limited listening tests.

### Next steps

1. Select one reference recording and one fixed Slovak text.
2. Generate outputs using the same conditions wherever possible.
3. Ask 3–5 people familiar with the reference speaker to compare the original and generated audio without being told which is which.
4. Record similarity ratings on a 1–5 scale and whether listeners identify the same speaker.
5. Evaluate the original and generated audio with an automated speaker-verification model. Record the model, score, and limitations.
6. Repeat with a second speaker to check whether the results generalize.
7. Verify API access, commercial usage terms, and cost before selecting a provider.

### Evaluation criteria

- Perceived speaker similarity
- Blind identification of the same speaker
- Automated speaker-similarity score
- Slovak intelligibility and naturalness
- Minimum reference audio duration
- API availability and cost

### Current status

Voice cloning feasibility is not yet confirmed. No provider has met a defined acceptance threshold because the threshold and evaluation procedure have not yet been established.
