"""Local Piper adapter with explicit CPU budgeting; no network calls."""
from pathlib import Path
import argparse,json,time,wave
import onnxruntime as ort
from piper.voice import PiperVoice
from piper.config import PiperConfig,SynthesisConfig
ap=argparse.ArgumentParser();ap.add_argument('episode');ap.add_argument('outdir');ap.add_argument('--threads',type=int,default=1);a=ap.parse_args()
ep=json.loads(Path(a.episode).read_text());out=Path(a.outdir);out.mkdir(exist_ok=True)
p=Path('/workspace/video-tools/piper-local/libritts/en-us-libritts-high.onnx')
opts=ort.SessionOptions();opts.intra_op_num_threads=a.threads;opts.inter_op_num_threads=1;opts.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
voice=PiperVoice(session=ort.InferenceSession(str(p),sess_options=opts,providers=['CPUExecutionProvider']),config=PiperConfig.from_dict(json.loads(Path(str(p)+'.json').read_text())))
config=SynthesisConfig(speaker_id=0,length_scale=1.60,normalize_audio=False)
for i,beat in enumerate(ep['beats']):
 dest=out/f'beat-{i:02}.wav';start=time.monotonic()
 if dest.exists():
  try:
   with wave.open(str(dest)) as prior:
    if prior.getnframes()==0 or len(prior.readframes(prior.getnframes()))!=prior.getnframes()*2:dest.unlink()
  except (wave.Error,EOFError):dest.unlink()
 if not dest.exists():
  with wave.open(str(dest),'wb') as wav:voice.synthesize_wav(beat['text'],wav,syn_config=config)
 print(str(dest),flush=True)
