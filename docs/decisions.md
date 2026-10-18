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
