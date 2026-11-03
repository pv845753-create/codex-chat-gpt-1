"""Copy reviewed deliverables into the local Git checkout. No network writes."""
from pathlib import Path
import json,hashlib,shutil
from produce import ROOT
OUT=Path('/workspace/codex-chat-gpt-1/series/season-01');OUT.mkdir(exist_ok=True,parents=True)
BASE='https://raw.githubusercontent.com/pv845753-create/codex-chat-gpt-1/refs/heads/codex/hardstart-season-01/series/season-01/'
rows=[];manifest=[]
paths=sorted(ROOT.glob('*/episode.json'));assert len(paths)==10
for path in paths:
 folder=path.parent;ep=json.loads(path.read_text());metrics=json.loads((folder/'metrics.json').read_text());verification=json.loads((folder/'verification.json').read_text())
 video=folder/f"{ep['id']}-{ep['slug'].removeprefix(ep['id']+'-')}-draft-en.mp4"
 assert video.exists() and float(verification['format']['duration'])>=300
 assert metrics['diagrams']==2
 streams=verification['streams'];video_stream=next(s for s in streams if s['codec_name']=='h264');audio_stream=next(s for s in streams if s['codec_name']=='aac')
 assert (video_stream['width'],video_stream['height'],video_stream['r_frame_rate'])==(1280,720,'24/1')
 assert audio_stream['sample_rate']=='48000'
 dst=OUT/folder.name;dst.mkdir(exist_ok=True)
 names=['episode.json','script-en.md','identity-pt.md','graphics.svg','youtube-en.md','project.md','metrics.json','verification.json','captions-en.srt','storyboard.jpg',video.name]
 for name in names:shutil.copyfile(folder/name,dst/name)
 sha=hashlib.sha256(video.read_bytes()).hexdigest();assert sha==hashlib.sha256((dst/video.name).read_bytes()).hexdigest()
 dur=float(verification['format']['duration']);secs=round(dur)
 item={'id':ep['id'],'title':ep['title'],'topic_pt':ep['topic_pt'],'vibe_pt':ep['vibe_pt'],'duration_seconds':dur,'duration':f'{secs//60}:{secs%60:02d}','words':metrics['words'],'diagrams':2,'file':f'{folder.name}/{video.name}','url':BASE+folder.name+'/'+video.name,'sha256':sha,'size_bytes':video.stat().st_size,'status':'Narrated limited-animation draft; not a final YouTube release.'}
 manifest.append(item)
 rows.append(f"| {ep['id']} | [{ep['title']}]({item['url']}) | {item['duration']} | [Roteiro]({folder.name}/script-en.md) · [Identidade]({folder.name}/identity-pt.md) |")
for name in ['SERIES-PLAN.md','TREND-EVIDENCE.md','VOICE-AND-ASSETS.md','slate.json']:shutil.copyfile(ROOT/name,OUT/name)
eng=OUT/'engine';eng.mkdir(exist_ok=True)
for path in (ROOT/'engine').iterdir():
 if path.suffix in ('.py','.md','.lock'):shutil.copyfile(path,eng/path.name)
for src,name in [(Path('/workspace/codex-chat-gpt-1/design.md'),'BRAND-DESIGN.md'),(Path('/workspace/codex-chat-gpt-1/EDITING_SKILL.md'),'EDITING-SKILL.md')]:shutil.copyfile(src,OUT/name)
# One representative visual per story, using its current props and palette.
import art
from PIL import Image,ImageDraw,ImageFont
sheet=Image.new('RGB',(1280,2000),'#0b0e14')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
scenes=['train','workbench','phone','arcade','projector','workbench','piano','workbench','bench','stage']
for i,path in enumerate(paths):
 ep=json.loads(path.read_text());frame=art.render_frame(ep,{'scene':scenes[i]},i,3,.55).resize((640,360));x=(i%2)*640;y=(i//2)*400;sheet.paste(frame,(x,y));d=ImageDraw.Draw(sheet);d.rectangle((x,y+307,x+640,y+400),fill='#0b0e14');d.text((x+18,y+331),ep['id']+'  '+ep['title'],font=font,fill='#e3dfcf')
sheet.save(OUT/'identities.jpg')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'README.md').write_text('''# Hardstart Films — 10 prévias narradas

**Os 10 MP4s estão disponíveis abaixo.** Cada vídeo tem mais de cinco minutos, narração sintética em inglês, música e efeitos originais, dois diagramas conceituais e direção visual própria. Clique no título para abrir ou baixar o MP4 completo.

São **prévias com animação limitada**, em 720p/24fps, com 12 desenhos por segundo. Ainda precisam de revisão humana integral de voz/mix, ajuste fino das legendas e refinamento de atuação antes de publicação. Não foram publicados no YouTube.

[Ver as 10 identidades](identities.jpg) · [Plano da série](SERIES-PLAN.md) · [Base da seleção de temas](TREND-EVIDENCE.md) · [Voz e licenças](VOICE-AND-ASSETS.md) · [Manual visual](BRAND-DESIGN.md)

A seleção usa sinais dos prints fornecidos; não é um ranking de tendências atuais. Os três últimos temas são apostas editoriais.

| Nº | MP4 completo | Duração | Produção |
| --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

## Verificação

Os arquivos finais foram verificados quanto a duração mínima, presença de vídeo H.264/áudio AAC e decodificação completa. A cópia entregue foi comparada por SHA-256; consulte [manifest.json](manifest.json). Isso não equivale a uma avaliação humana de cada minuto. As legendas têm timing aproximado por frase.

## Som

A voz foi sintetizada localmente com Piper/LibriTTS high, speaker0. Atribuição: Heiga Zen et al., LibriTTS (2019), dataset CC BY4.0, http://www.openslr.org/60/. Consulte os detalhes de origem e transformação em VOICE-AND-ASSETS.md. Música e efeitos são procedurais originais; nenhuma faixa da Epidemic Sound foi usada.
''')
summary={'videos':len(manifest),'total_seconds':sum(m['duration_seconds'] for m in manifest),'minimum_seconds':min(m['duration_seconds'] for m in manifest),'maximum_seconds':max(m['duration_seconds'] for m in manifest),'words':sum(m['words'] for m in manifest),'diagrams':sum(m['diagrams'] for m in manifest),'total_bytes':sum(m['size_bytes'] for m in manifest)}
(OUT/'production-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
for m in manifest:print(m['id'],m['duration'],m['title'],flush=True)
