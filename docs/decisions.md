# Decisions

## D-001: Voice cloning strategy

**Status:** Provisional

- Voice cloning is the primary research goal for LinguaVoice.
- Standard Slovak TTS remains the fallback.
- No voice cloning provider has been selected as the final solution.
- The preferred approach must work with a short audio reference, without requiring users to record a separate long voice dataset.

## D-002: Voice similarity evaluation

**Status:** Planned

- Do not evaluate voice similarity by personal impression alone.
- Compare providers using the same reference audio and target text.
- Combine blind listener evaluations with an automated speaker-similarity metric.
- Automated scores must be interpreted cautiously, especially across different languages.

## D-003: Provider selection

**Status:** Open

- ElevenLabs Instant, Cartesia, and Polyvox have been tested.
- Polyvox is the current best candidate based on preliminary listening tests.
- Further testing is required before choosing a provider for implementation.
- API availability, commercial licensing, and cost must be verified before integration.

## D-004: Research before implementation

- Do not build the full dubbing pipeline around an unvalidated voice cloning provider.
- Keep provider-specific code isolated so the implementation can be changed without redesigning the application.

## D-005: Function pipeline, not a chat model

**Status:** Accepted

- The application orchestrates named functions. It does not send a recording to a general AI model with a request to return dubbed audio.
- ASR, translation, and synthesis models may be called only from their own function, with fixed inputs and structured outputs.
- Alignment, duration limits, job status, and metrics are application logic.
## Stage 2: voice cloning provider

**Decision.** Primary clone: XTTS-v2 (open model, runs locally, no API key).
Fallback: XTTS-v2 built-in voice for now; revisit at Stage 5 if its quality
stays poor.

**Why.** No paid account or API key needed, works offline, fits the limited
API budget, and the result is "similar, not identical", which is acceptable
for the MVP.

**Consequences.**
- XTTS needs Python 3.10-3.12, while the main backend runs on 3.14. XTTS lives
  in a separate environment (`.venv-tts`, Python 3.11); how the backend calls
  it (subprocess or small separate service) is decided at Stage 5.
- Model weights use the Coqui Public Model License (non-commercial); fine for
  this educational project, not for commercial use.
- Voice samples are real people's voices: they stay out of git
  (`backend/scripts/samples_raw/` is ignored) and are used only with the
  speaker's consent.
