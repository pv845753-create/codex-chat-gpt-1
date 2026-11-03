# Voice and assets provenance

## English narration
Synthetic U.S. English voice generated locally with Piper. No voice cloning requested, no voice from a reference YouTube channel, no paid remote service.

- Runtime source: https://github.com/rhasspy/piper/releases/tag/v0.0.2
- Model asset: https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-libritts-high.tar.gz
- Model: LibriTTS high; speaker ID 0; 22,050 Hz.
- Model card distributed with the official archive: trained from scratch on LibriTTS train-clean-360; dataset license CC BY 4.0.
- Dataset: Heiga Zen et al., *LibriTTS: A Corpus Derived from LibriSpeech for Text-to-Speech* (2019), http://www.openslr.org/60/.
- License reference: https://creativecommons.org/licenses/by/4.0/.
- Transformation: text-to-speech synthesis, pacing, joins with short fades, mixing and loudness normalization.

The card is retained locally under /workspace/video-tools/piper-local/libritts/MODEL_CARD. Runtime binaries and model weights are not included in the video delivery repository.

Ryan was tested but rejected because its card states CC BY-NC-SA 4.0 for the dataset. Danny was not used because its card does not provide sufficiently clear license information and says it was fine-tuned from Ryan. Neither voice is used in this series.

## Music and sound effects
Original procedural audio synthesized by engine/produce.py. No third-party songs or samples; no Epidemic Sound audio. The Epidemic Sound integration remains unavailable. Music/effects stems are retained per episode for remixing.

## Illustration and graphics
Original 2D programmatic artwork in engine/art.py. No extracted frames or audio from reference channels. Each episode has its own palette, story, two conceptual diagrams and sound motif. This is limited animation, not a claim of hand-animated cinematic final quality.

## Typography
DejaVu Sans from the installed system fonts. Preserve the DejaVu/Bitstream font license when redistributing font binaries. No font binary is included in the delivery.

## Review status
Narration is synthetic. Caption timing is approximate at phrase level from per-beat audio durations; not forced word alignment. Full-file decoding, stream metadata, duration and audio presence are checked by the build. Representative frames are inspected. No claim of a human listening review of every minute or of YouTube publication.
