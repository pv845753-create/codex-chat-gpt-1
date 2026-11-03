# Production engine

This is an original limited-animation pipeline for narrated workprints, not a replacement for final character animation and sound direction.

## Runtime
Linux, Python 3.12, FFmpeg/ffprobe, DejaVu Sans system fonts, Pillow, NumPy and SciPy. The current main venv is `/workspace/video-tools/venv`. The separate speech venv is `/workspace/video-tools/tts-venv`; pinned speech packages are in `voice-requirements.lock`.

The voice model is the official Piper v0.0.2 `voice-en-us-libritts-high.tar.gz`. Retrieve only through verified HTTPS, preserve its model card, and read `../VOICE-AND-ASSETS.md` for attribution. Model weights and Piper binaries are not distributed in this repository. Downloading and installing an environment is distinct from running this build.

## Build order
1. Place production folders under `/workspace/video-projects/hardstart-season-01/edit/`, preserving the existing files. The code uses this workspace's voice/font paths.
2. Run `produce.py voice <episode-folders> --jobs 3` from the main venv. This caches each per-beat voice recording and emits an audio-based timeline. Explicit ORT thread limits respect the current four-CPU quota.
3. Run `produce.py render <episode-folders> --jobs 1`. It renders at native 1280×720 with 12 drawn frames per second, output as a 24fps H.264 stream. Caption text is added last. Stems remain separate.
4. When all picture refinements are finished, run `finalize_audio.py`. It mixes music/effects under speech, muxes AAC, checks minimum duration, inspects stream metadata and decodes every delivered MP4.
5. Run `publish_pack.py` to copy finished files into the repository delivery folder and refresh its index. This copies files only: it does not push or publish anything.

The first two drafts were synthesized with the legacy native Piper runtime; subsequent drafts use the Python adapter and the same voice model/speaker. Captions use approximate phrase timing from synthesized per-beat audio durations; no word-level forced alignment is claimed. Sources, scores and character motion should receive further human review before a public YouTube release.
