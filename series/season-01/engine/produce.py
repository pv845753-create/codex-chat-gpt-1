from pathlib import Path
import argparse,concurrent.futures,json,math,subprocess,wave,time,os,bisect,textwrap,hashlib
import numpy as np
from scipy.ndimage import uniform_filter1d
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
PIPER=Path('/workspace/video-tools/piper-local')
MODEL=PIPER/'libritts/en-us-libritts-high.onnx'
RATE=22050

def wavread(path):
 with wave.open(str(path)) as w:
  assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getframerate()==RATE
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768

def wavwrite(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((np.clip(a,-.99,.99)*32767).astype('<i2').tobytes())

def voice_episode(folder):
 ep=json.loads((folder/'episode.json').read_text());vd=folder/'voice';vd.mkdir(exist_ok=True)
 texts=[b['text'].strip() for b in ep['beats']]
 fingerprint=hashlib.sha256(('\n'.join(texts)+'libritts-high|speaker0|scale1.6').encode()).hexdigest()
 record=vd/'record.json'
 if record.exists() and json.loads(record.read_text()).get('fingerprint')==fingerprint:
  files=[Path(p) for p in json.loads(record.read_text())['files']]
 else:
  print('VOICE START',folder.name,flush=True)
  cmd=['/workspace/video-tools/tts-venv/bin/python',str(ROOT/'engine/synthesize.py'),str(folder/'episode.json'),str(folder/'voice-python'),'--threads','1']
  r=subprocess.run(cmd,input='\n'.join(texts)+'\n',text=True,capture_output=True,check=True,env={**os.environ,'OMP_NUM_THREADS':'1'})
  (vd/'synthesis.log').write_text(r.stderr)
  files=[Path(p.strip()) for p in r.stdout.splitlines() if p.strip().endswith('.wav')]
  assert len(files)==len(texts),(folder,len(files),len(texts))
  record.write_text(json.dumps({'fingerprint':fingerprint,'files':[str(p) for p in files]},indent=2))
 arrays=[wavread(p) for p in files]
 spoken=sum(len(a)/RATE for a in arrays)
 # Natural boundaries; no repeated footage to hit a duration requirement.
 pause=.42
 total=spoken+pause*len(arrays)+2.4
 if total<305:
  # Preserve pitch while slowing the spoken performance, not extending still frames.
  factor=(spoken)/(310-pause*len(arrays)-2.4)
  slowed=[]
  for i,p in enumerate(files):
   dest=vd/f'paced-{i:02}.wav'
   subprocess.run(['ffmpeg','-y','-v','error','-i',str(p),'-af',f'atempo={factor:.7f}','-ac','1','-ar',str(RATE),str(dest)],check=True)
   slowed.append(wavread(dest))
  arrays=slowed
 timeline=[];segments=[];offset=1.0
 segments.append(np.zeros(RATE,dtype=np.float32))
 for i,(b,a) in enumerate(zip(ep['beats'],arrays)):
  fade=min(int(.03*RATE),len(a)//4);a=a.copy();a[:fade]*=np.linspace(0,1,fade);a[-fade:]*=np.linspace(1,0,fade)
  duration=len(a)/RATE
  timeline.append({**b,'index':i,'start':offset,'speech_end':offset+duration,'end':offset+duration+pause})
  segments.extend([a,np.zeros(round(pause*RATE),dtype=np.float32)]);offset+=duration+round(pause*RATE)/RATE
 segments.append(np.zeros(round(1.4*RATE),dtype=np.float32));voice=np.concatenate(segments);dur=len(voice)/RATE
 timeline[0]['start']=0;timeline[-1]['end']=dur
 wavwrite(folder/'voice.wav',voice)
 (folder/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
 (folder/'narration-en.txt').write_text('\n\n'.join(texts))
 cues=[]
 for b in timeline:
  words=b['text'].split();chunks=[words[j:j+9] for j in range(0,len(words),9)]
  for j,c in enumerate(chunks):
   start=b['start']+j*(b['speech_end']-b['start'])/len(chunks)
   end=b['start']+(j+1)*(b['speech_end']-b['start'])/len(chunks)
   cues.append([start,end,' '.join(c)])
 (folder/'cues.json').write_text(json.dumps(cues,ensure_ascii=False))
 def st(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 (folder/'captions-en.srt').write_text('\n\n'.join(f'{i+1}\n{st(a)} --> {st(b)}\n{t}' for i,(a,b,t) in enumerate(cues))+'\n')
 score=np.zeros(len(voice),dtype=np.float32);sfx=np.zeros_like(score);rng=np.random.default_rng(int(ep['id']))
 number=int(ep['id']);base=[110,130.81,98,146.83,123.47,116.54,130.81,103.83,146.83,130.81][number-1]
 def add(dst,t,snd):
  k=max(0,int(t*RATE));n=min(len(snd),len(dst)-k)
  if n>0:dst[k:k+n]+=snd[:n]
 def tone(hz,seconds,amp,pad=False):
  tt=np.arange(int(seconds*RATE))/RATE
  env=np.sin(np.pi*tt/seconds)**1.5 if pad else (1-np.exp(-tt*65))*np.exp(-tt*3/seconds)
  # Evolving pad and damped partials, no third-party audio samples.
  return (amp*env*(np.sin(2*np.pi*hz*tt)+(.18 if pad else .10)*np.sin(2*np.pi*hz*2.003*tt))).astype(np.float32)
 cadence=[2,3,2.8,1.5,2.5,2,3.4,4,2.8,2.6][number-1]
 for t in np.arange(0,dur,8):
  ratio=[1,.89,.79,.89][int(t/8)%4];chord=[base*ratio,base*ratio*1.25,base*ratio*1.5]
  for hz in chord:add(score,t,tone(hz,9,.010,pad=True))
 for n,t in enumerate(np.arange(0,dur,cadence)):
  if dur*.39<t<dur*.40:continue
  hz=base*[2,2.5,3,2.5,2,3,4,3][n%8]
  add(score,t,tone(hz,1.5,.018 if number not in (7,8,9) else .013))
 for b in timeline:
  t=b['start'];scene=b['scene']
  if scene in ('phone','phoneaway'):add(sfx,t+.7,tone(740+number*13,.18,.055))
  if scene=='clock':
   for j in range(int(b['end']-t)):add(sfx,t+j,tone(1800,.025,.035))
  if scene in ('write','workbench','desk','notes','organize','books'):
   for j in range(5):
    n=int(.065*RATE);noise=rng.normal(0,.016,n)*np.sin(np.linspace(0,np.pi,n));add(sfx,t+1.3+j*.58,noise)
  if scene in ('rain','window','street','train'):
   n=int((b['end']-t)*RATE);noise=rng.normal(0,.003,n);noise=np.convolve(noise,np.ones(5)/5,'same');noise*=np.minimum(np.arange(n)/RATE/.3,1)*np.minimum(np.arange(n)[::-1]/RATE/.3,1);add(sfx,t,noise)
  if scene in ('stairs','door','shoes'):
   for j in range(6):add(sfx,t+j*.66,tone(65,.13,.07))
  if scene in ('piano','stage'):
   for j,hz in enumerate([base*2,base*2.5,base*3]):add(sfx,t+j*.8,tone(hz,1.4,.035))
  if scene=='diagram':
   nodes=ep['diagrams'][int(b.get('graphic_id',0))]['nodes']
   for j in range(len(nodes)):add(sfx,t+j*.8,tone(330+j*83,.19,.035))
 for a in (score,sfx):
  n=min(2*RATE,len(a));a[:n]*=np.linspace(0,1,n);a[-n:]*=np.linspace(1,0,n)
 # Smooth voice-driven ducking avoids music competing with the narrator.
 envelope=np.abs(voice);win=np.ones(1103)/1103
 envelope=uniform_filter1d(envelope,size=1103,mode='nearest');duck=np.where(envelope>.012,.43,1.0)
 duck=uniform_filter1d(duck,size=4411,mode='nearest')
 mix=voice*.91+score*duck+sfx
 wavwrite(folder/'music-original.wav',score);wavwrite(folder/'effects-original.wav',sfx);wavwrite(folder/'mix.wav',mix)
 metrics={'duration_seconds':dur,'spoken_seconds':sum(len(a)/RATE for a in arrays),'words':sum(len(t.split()) for t in texts),'beats':len(timeline),'diagrams':sum(b['scene']=='diagram' for b in timeline),'voice':'Piper LibriTTS high, speaker 0, synthetic U.S. English','voice_dataset_license':'CC BY 4.0 per official model card','status':'narrated production draft','caption_timing':'Approximate phrase timing from per-beat synthesized audio, not forced word alignment.'}
 assert dur>=300,(folder,dur)
 (folder/'metrics.json').write_text(json.dumps(metrics,indent=2))
 print('VOICE READY',folder.name,round(dur,1),'seconds',flush=True)
 return folder

def render_episode(folder):
 import art
 ep=json.loads((folder/'episode.json').read_text());tl=json.loads((folder/'timeline.json').read_text());cues=json.loads((folder/'cues.json').read_text());dur=json.loads((folder/'metrics.json').read_text())['duration_seconds']
 ends=[b['end'] for b in tl];cends=[c[1] for c in cues]
 FPS=12;count=math.ceil(dur*FPS);W,H=1280,720
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28)
 renderout=folder/'picture.mp4';cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-vf','fps=24','-c:v','libx264','-threads','2','-preset','veryfast','-crf','23','-pix_fmt','yuv420p',str(renderout)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 print('RENDER START',folder.name,round(dur,1),flush=True)
 next_progress=0
 for fr in range(count):
  t=fr/FPS;ix=min(bisect.bisect_right(ends,t),len(tl)-1);b=tl[ix];local=max(0,t-b['start']);progress=min(1,local/max(.1,b['end']-b['start']))
  image=art.render_frame(ep,b,ix,local,progress,W,H)
  assert image.size==(W,H)
  d=ImageDraw.Draw(image);d.rectangle((0,607,W,H),fill='#0B0E14')
  ci=min(bisect.bisect_right(cends,t),len(cues)-1);cue=cues[ci]
  if cue[0]<=t<=cue[1]+.1:
   for j,line in enumerate(textwrap.wrap(cue[2],69)):
    box=d.textbbox((0,0),line,font=font);d.text(((W-box[2])/2,625+j*35),line,font=font,fill='#EFEADC')
  proc.stdin.write(image.convert('RGB').tobytes())
  if t>=next_progress:print('RENDER',folder.name,round(t), '/',round(dur),flush=True);next_progress+=60
 proc.stdin.close()
 if proc.wait():raise RuntimeError('Picture render failed '+folder.name)
 output=folder/f"{ep['id']}-{ep['slug'].removeprefix(ep['id']+'-')}-draft-en.mp4"
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(renderout),'-i',str(folder/'mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:a','aac','-b:a','160k','-t',f'{dur:.4f}','-movflags','+faststart',str(output)],check=True)
 # A representative contact sheet, not an assertion that every action was visually reviewed.
 sheet=Image.new('RGB',(1280,1080))
 sample=[0,len(tl)//5,2*len(tl)//5,3*len(tl)//5,4*len(tl)//5,len(tl)-1]
 for j,si in enumerate(sample):
  b=tl[si];im=art.render_frame(ep,b,si,2,.4,W,H).resize((640,360));sheet.paste(im,((j%2)*640,(j//2)*360))
 sheet.save(folder/'storyboard.jpg')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(output)]))
 subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(output),'-f','null','-'],check=True)
 assert float(probe['format']['duration'])>=300
 (folder/'verification.json').write_text(json.dumps(probe,indent=2))
 print('COMPLETE',folder.name,output.name,probe['format'],flush=True)
 return output

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['voice','render']);ap.add_argument('folders',nargs='+');ap.add_argument('--jobs',type=int,default=2);args=ap.parse_args()
 folders=[Path(f).resolve() for f in args.folders]
 fn=voice_episode if args.mode=='voice' else render_episode
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
  future={pool.submit(fn,p):p for p in folders}
  failed=[]
  for f in concurrent.futures.as_completed(future):
   try:f.result()
   except Exception as e:print('FAILED',future[f],repr(e),flush=True);failed.append(str(future[f]))
 if failed:raise SystemExit('Failed: '+','.join(failed))
