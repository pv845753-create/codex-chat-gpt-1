"""Finalize original stems after picture lock, then verify the delivered bitstreams."""
from pathlib import Path
import json,subprocess
import numpy as np
from scipy.ndimage import uniform_filter1d
from produce import ROOT,wavread,wavwrite,RATE
for path in sorted(ROOT.glob('*/episode.json')):
 folder=path.parent;ep=json.loads(path.read_text());voice=wavread(folder/'voice.wav');music=wavread(folder/'music-original.wav');effects=wavread(folder/'effects-original.wav')
 assert len(voice)==len(music)==len(effects)
 rms=float(np.sqrt(np.mean(voice*voice)))
 gain=min(10**(-20.5/20)/max(1e-8,rms),.94/max(1e-8,float(np.max(np.abs(voice)))))
 voice=voice*gain
 env=uniform_filter1d(np.abs(voice),1103,mode='nearest');duck=uniform_filter1d(np.where(env>.012,.62,1.0),4411,mode='nearest')
 arc=np.linspace(1.0,1.30,len(voice),dtype=np.float32)
 mix=voice+music*2.0*duck*arc+effects*1.25
 wavwrite(folder/'mix.wav',mix)
 m=json.loads((folder/'metrics.json').read_text());out=folder/f"{ep['id']}-{ep['slug'].removeprefix(ep['id']+'-')}-draft-en.mp4"
 subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-i',str(folder/'picture.mp4'),'-i',str(folder/'mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:a','aac','-ar','48000','-b:a','160k','-t',f"{m['duration_seconds']:.4f}",'-movflags','+faststart',str(out)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels','-of','json',str(out)]))
 assert float(probe['format']['duration'])>=300
 assert {s['codec_name'] for s in probe['streams']}=={'h264','aac'}
 subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(out),'-f','null','-'],check=True)
 (folder/'verification.json').write_text(json.dumps(probe,indent=2))
 m['voice_gain_before_mix']=gain
 m['mix_revision']='Voice-ducked original score, gradual musical lift, synchronized synthesized effects; target -16 LUFS and -1.5dBTP.';(folder/'metrics.json').write_text(json.dumps(m,indent=2))
 print('FINAL AUDIO AND DECODE VERIFIED',folder.name,probe['format'],flush=True)
print('ALL TEN FINAL FILES VERIFIED',flush=True)
