"""Original native-resolution illustration engine for Hardstart Films.

API: render_frame(episode, beat, index, local, progress, width=1280, height=720).
The lower 16% is reserved for editorial captions added by the caller.
No network, samples, external artwork, or mutable process-wide drawing state.
"""
from functools import lru_cache
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CREAM='#e0dccb'; INK='#85898d'; BODY='#35414a'; DARK='#111821'
SCENES=['desk','phone','clock','organize','window','bed','notes','mirror','phoneaway','kitchen','write','send','door','arcade','street','stairs','train','workbench','bench','water','calendar','rain','projector','stage','piano','books','shoes','sofa','diagram','end']

def rgb(c):
    try:return tuple(int(c.lstrip('#')[i:i+2],16) for i in (0,2,4))
    except:return (93,158,151)
def blend(a,b,t):
    a=rgb(a) if isinstance(a,str) else a;b=rgb(b) if isinstance(b,str) else b
    return tuple(int(x*(1-t)+y*t) for x,y in zip(a,b))
def ease(t):return 1-(1-max(0,min(1,t)))**3
@lru_cache(maxsize=128)
def font(n,bold=False,scale=1):return ImageFont.truetype(BOLD if bold else FONT,max(1,round(n*scale)))

class D:
    def __init__(self,im):self.im=im;self.s=im.width/960;self.d=ImageDraw.Draw(im)
    def pts(self,p):return [(round(x*self.s),round(y*self.s)) for x,y in p]
    def box(self,b):return tuple(round(v*self.s) for v in b)
    def line(self,p,c,w=2):
        p=self.pts(p);w=max(1,round(w*self.s));self.d.line(p,fill=c,width=w,joint='curve')
        if w>3:
            r=w/2
            for x,y in (p[0],p[-1]):self.d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    def poly(self,p,c,outline=None,w=1):self.d.polygon(self.pts(p),fill=c,outline=outline,width=max(1,round(w*self.s)))
    def rr(self,b,r,c,outline=None,w=1):self.d.rounded_rectangle(self.box(b),round(r*self.s),fill=c,outline=outline,width=max(1,round(w*self.s)))
    def rect(self,b,c,outline=None,w=1):self.d.rectangle(self.box(b),fill=c,outline=outline,width=max(1,round(w*self.s)))
    def ellipse(self,b,c,outline=None,w=1):self.d.ellipse(self.box(b),fill=c,outline=outline,width=max(1,round(w*self.s)))
    def arc(self,b,a,z,c,w=2):self.d.arc(self.box(b),a,z,fill=c,width=max(1,round(w*self.s)))
    def text(self,p,t,n=18,c=CREAM,b=False,anchor=None):self.d.text(self.pts([p])[0],str(t),font=font(n,b,self.s),fill=c,anchor=anchor)
    def center(self,t,y,n=22,c=CREAM,b=False):self.text((480,y),t,n,c,b,'mt')

def fit_lines(text,n=30,maxw=760,limit=3):
    maxchars=max(10,int(maxw/(n*.62)))
    lines=textwrap.wrap(str(text),maxchars)
    return lines[:limit]

@lru_cache(maxsize=64)
def background(accent,secondary,kind,w,h):
    """Native-resolution painterly pools of light and low-amplitude grain."""
    yy,xx=np.mgrid[0:h,0:w];x=xx/w;y=yy/h
    base=np.zeros((h,w,3),dtype=np.float32)+np.array([12,17,23])
    a=np.array(rgb(accent));s=np.array(rgb(secondary))
    if kind in ('stage','street','bench','door'):px,py=.68,.34
    else:px,py=.67,.51
    pool=np.exp(-(((x-px)/.36)**2+((y-py)/.52)**2)*2.1)
    cool=np.exp(-(((x-.22)/.38)**2+((y-.28)/.58)**2)*2.0)
    base+=pool[...,None]*s*.21+cool[...,None]*a*.10
    vign=np.clip(1-.35*((x-.5)**2+(y-.48)**2),.72,1)
    rng=np.random.default_rng(23);noise=rng.normal(0,.65,(h,w,1))
    base=base*vign[...,None]+noise
    im=Image.fromarray(np.uint8(np.clip(base,0,255)),'RGB');d=D(im)
    d.poly([(0,419),(960,419),(960,540),(0,540)],'#121923')
    d.line([(0,418),(960,418)],'#424a53',1.4)
    for j in range(9):
        q=j*130-40;d.line([(q,418),(q+(q-480)*.5,540)],'#202733',1)
    # Fine wall moulding and corner geometry hold the space without clutter.
    d.line([(39,76),(39,417)],'#252e3a',1);d.line([(915,76),(915,417)],'#252e3a',1)
    d.line([(0,409),(960,409)],'#202833',1)
    return im


def shadow(d,x,y,rx=50,ry=7):
    d.ellipse((x-rx,y-ry,x+rx,y+ry),'#0b1016')
    d.ellipse((x-rx*.75,y-ry*.7,x+rx*.75,y+ry*.7),'#080c11')
def window(d,x=702,y=104,w=142,h=154,t=0,rain=False,day=False):
    d.rr((x-6,y-6,x+w+6,y+h+6),13,'#171e29','#424e5f',2)
    d.rr((x,y,x+w,y+h),8,'#29394d' if day else '#17263b','#697786',2)
    d.ellipse((x+w-44,y+19,x+w-18,y+45),'#d5dbd7')
    for j in range(5):
        bx=x+9+j*27;bh=21+(j*13)%47
        d.rect((bx,y+h-bh,bx+19,y+h),'#202e40')
        for q in range(2):d.rect((bx+5,y+h-bh+7+q*12,bx+8,y+h-bh+11+q*12),'#8a805b')
    d.line([(x+w*.5,y),(x+w*.5,y+h)],'#6d7c8b',3)
    d.line([(x,y+h*.52),(x+w,y+h*.52)],'#6d7c8b',3)
    d.line([(x+7,y+7),(x+48,y+7)],'#a6b3bc',1)
    if rain:
        for j in range(18):
            px=x+6+(j*31)%(w-12);py=y+5+(j*47+t*65)%(h-17)
            d.line([(px,py),(px-3,py+13)],'#7890a0',1)

def clock(d,x=208,y=154,r=35,t=0,accent='#cda76b'):
    d.ellipse((x-r-4,y-r-4,x+r+4,y+r+4),'#141b24','#525b67',2)
    d.ellipse((x-r,y-r,x+r,y+r),'#c9c9b9','#8f938d',1)
    for j in range(12):
        a=j*math.pi/6
        d.line([(x+math.sin(a)*(r-8),y-math.cos(a)*(r-8)),(x+math.sin(a)*(r-4),y-math.cos(a)*(r-4))],'#535e60',2 if r>60 else 1)
    a=t*.45
    d.line([(x,y),(x+math.sin(a)*(r-10),y-math.cos(a)*(r-10))],'#414d53',3)
    d.line([(x,y),(x-r*.37,y-r*.30)],'#414d53',4)
    d.ellipse((x-3,y-3,x+3,y+3),accent)

def mug(d,x,y,c='#718b94',s=1):
    d.arc((x+15*s,y-23*s,x+36*s,y-4*s),-90,95,c,3)
    d.rr((x,y-27*s,x+23*s,y),4*s,c,'#94a2a4',1)
    d.ellipse((x+2*s,y-29*s,x+21*s,y-24*s),'#363d42')

def lamp(d,x,y,accent):
    d.ellipse((x-25,y-5,x+26,y+4),'#7a7c76')
    d.line([(x,y-4),(x,y-86),(x-31,y-121)],'#89908b',5)
    d.poly([(x-54,y-119),(x-27,y-135),(x-7,y-111),(x-40,y-103)],'#596b73','#91a2a6',1)
    d.line([(x-40,y-104),(x-10,y-111)],accent,4)

def plant(d,x,y,s=1):
    d.poly([(x-18*s,y-27*s),(x+18*s,y-27*s),(x+12*s,y),(x-12*s,y)],'#58635d','#798277',1)
    d.line([(x,y-26*s),(x-3*s,y-91*s)],'#587963',3)
    for j in range(5):
        px=x-3*s;py=y-(37+j*11)*s;side=1 if j%2 else -1
        d.ellipse((min(px,px+side*24*s),py-10*s,max(px,px+side*24*s),py+2*s),'#4a6a5b')

def character(d,x=370,y=303,t=0,pose='stand',accent='#62a39b',scale=1,mood='tired',face=1):
    """Own character: soft head, side tuft, teal neckerchief. Coordinates at pelvis."""
    def pt(a,b):return (x+a*scale*face,y+b*scale)
    def bone(coords,col,w):
        ps=[pt(a,b) for a,b in coords];d.line(ps,'#222d36',w*scale+3*scale);d.line(ps,col,w*scale)
    # Ground and seated stance use stable feet.
    seated=pose in ('sit','phone','type','read','play')
    legstep=math.sin(t*5)*13 if pose=='walk' else 0
    if seated:
        legs=[[(-13,20),(20,42),(22,89)],[(13,20),(43,45),(46,89)]]
        shoes=[(22,89),(46,89)]
    else:
        legs=[[(-13,22),(-16+legstep*.5,56),(-22+legstep,94)],[(13,22),(16-legstep*.5,56),(22-legstep,94)]]
        shoes=[(-22+legstep,94),(22-legstep,94)]
    shadow(d,x+12*scale,y+99*scale,50*scale,6*scale)
    for leg in legs:bone(leg,'#394956',15)
    for sx,sy in shoes:
        xx,yy=pt(sx,sy);d.rr((xx-10*scale,yy-5*scale,xx+19*scale,yy+7*scale),5*scale,blend(accent,'#4a5a61',.4),'#81928f',1)
        d.line([(xx-5*scale,yy+5*scale),(xx+18*scale,yy+5*scale)],'#a8b2ac',1)
    # Hoodie silhouette, little shading and distinct soft side light.
    left,top=pt(-30,-37);right,bottom=pt(31,30)
    if left>right:left,right=right,left
    d.rr((left,top,right,bottom),22*scale,BODY,'#7a8388',1.5)
    d.line([pt(-22,-29),pt(-24,18)],'#53616b',3*scale)
    d.rr((x-14*scale,y+2*scale,x+16*scale,y+18*scale),4*scale,'#2d3943','#515d64',1)
    d.line([pt(-9,-16),pt(-9,-4)],'#a0aaa8',1);d.line([pt(11,-16),pt(11,-4)],'#a0aaa8',1)
    # Head outline irregular by design, not a perfect icon circle.
    hx=x;hy=y-78*scale
    d.ellipse((hx-36*scale,hy-38*scale,hx+36*scale,hy+32*scale),CREAM,'#afb4aa',1.8)
    d.arc((hx-33*scale,hy-34*scale,hx+32*scale,hy+29*scale),80,190,'#a2aba6',2*scale)
    d.poly([pt(-23,-105),pt(-18,-124),pt(-6,-112),pt(4,-112)],CREAM,'#9fa9a5',1)
    # Face looks toward action, with blink and expression.
    blick=t%5.3<.16
    for dx in [-13,13]:
        ex=x+(dx+face*2)*scale;ey=y-81*scale
        if blick:d.line([(ex-6*scale,ey),(ex+6*scale,ey)],'#26323a',2*scale)
        else:
            d.ellipse((ex-7*scale,ey-6*scale,ex+7*scale,ey+5*scale),'#f2f0de','#adb2a8',1)
            d.ellipse((ex-2*scale+face*scale,ey-3*scale,ex+3*scale+face*scale,ey+3*scale),'#26313a')
            if mood in ('tired','sad'):d.line([(ex-7*scale,ey-5*scale),(ex+7*scale,ey-4*scale)],'#8a928c',2*scale)
        slope=(3 if dx<0 else -3) if mood in ('sad','tired') else (-2 if dx<0 else 2)
        d.line([(ex-8*scale,ey-15*scale+slope*scale),(ex+7*scale,ey-15*scale-slope*scale)],'#354047',2.6*scale)
    d.line([pt(-5,-60),pt(4,-62 if mood in ('tired','sad') else -59),pt(9,-59)],'#49524f',2*scale)
    d.poly([pt(-26,-42),pt(27,-42),pt(18,-27),pt(-19,-31)],accent)
    d.poly([pt(14,-32),pt(25,-31),pt(31,-8),pt(15,-18)],blend(accent,'#15232b',.25))
    # Arms sit on top so hands can contact props.
    if pose=='type':
        dy=math.sin(t*13)*1.8
        arms=[[(-27,-23),(-34,4),(18,7+dy)],[(27,-23),(48,-3),(76,0-dy)]]
    elif pose=='phone':arms=[[(-27,-24),(-31,6),(-5,13)],[(27,-24),(43,-2),(20,-47)]]
    elif pose in ('read','play'):arms=[[(-27,-23),(-21,8),(8,-2)],[(27,-23),(48,1),(34,-5)]]
    elif pose=='wave':arms=[[(-27,-23),(-36,3),(-31,24)],[(27,-23),(47,-55),(48,-81)]]
    elif pose=='reach':
        q=ease((t%4)/2);arms=[[(-27,-23),(-31,5),(-25,28)],[(27,-23),(47,-13),(48+30*q,-17)]]
    elif pose=='handhead':arms=[[(-27,-23),(-49,-50),(-23,-95)],[(27,-23),(38,5),(30,29)]]
    else:
        swing=math.sin(t*5)*9 if pose=='walk' else 0
        arms=[[(-27,-23),(-36,4),(-32+swing,27)],[(27,-23),(38,5),(32-swing,28)]]
    for a in arms:
        bone(a,CREAM,10)
        xx,yy=pt(*a[-1]);d.ellipse((xx-6*scale,yy-5*scale,xx+6*scale,yy+5*scale),CREAM,'#a7ada3',1)
    if pose=='phone':
        xx,yy=pt(18,-61);d.rr((xx-10*scale,yy-8*scale,xx+12*scale,yy+27*scale),4*scale,'#6d9eae','#bdd0cf',1)
        d.line([(xx-5*scale,yy-3*scale),(xx+6*scale,yy-3*scale)],'#d2e4df',1)
    if pose=='read':
        xx,yy=pt(12,-3);d.poly([(xx-20*scale,yy-13*scale),(xx,yy-8*scale),(xx+20*scale,yy-14*scale),(xx+17*scale,yy+12*scale),(xx,yy+16*scale),(xx-20*scale,yy+9*scale)],'#c8c0a6','#777f78',1)


def desk_set(d,t,accent,secondary,working=True):
    # Lower-mid frame furniture, tools and source-motivated desk lamp.
    d.rr((375,318,799,334),5,'#74634e','#9c8a6e',1)
    for x in (397,774):d.line([(x,334),(x,417)],'#635e56',7)
    d.rr((480,204,701,311),8,'#26343f','#8b9ba2',2)
    d.rect((491,216,690,299),'#d3d5c6')
    d.line([(469,316),(712,316)],'#94a19e',5)
    if working:
        for n in range(min(6,1+int(t/1.1))):
            d.line([(509,233+n*10),(548+min(121,int(t*19)),233+n*10)],'#5f726d',2)
    else:d.line([(509,232),(509,249)],'#587b73',2)
    lamp(d,755,317,secondary);mug(d,429,317,accent)
    d.rr((318,340,379,394),10,'#27333d','#5c6c78',2)
    d.line([(350,393),(350,418)],'#5a6670',5)
    d.line([(328,419),(372,419)],'#71808a',3)


def phone_macro(d,t,accent,secondary,index):
    shadow(d,480,421,125,10)
    d.rr((364,82,596,422),31,'#2b3440','#899aab',3)
    d.rr((375,94,585,409),24,'#152431')
    d.rr((442,98,519,109),5,'#0c1119')
    d.text((397,125),'FOR YOU',16,'#c5d0cc',True)
    sy=155-(t*19)%78
    for j in range(4):
        y=sy+j*85
        if y<133 or y>368:continue
        d.rr((389,y,571,min(y+71,391)),10,blend(accent,'#17242f',.73),'#536c76',1)
        d.ellipse((400,y+10,431,y+41),blend(secondary,'#bec8bb',.35))
        for n in range(2):d.line([(443,y+15+n*12),(551,y+15+n*12)],'#86a5a8',3)
        d.line([(402,y+56),(549,y+56)],'#5c7983',2)
    for j in range(4):d.ellipse((405+j*43,389,410+j*43,394),accent)
    # A clear hand/thumb interaction, not just a glowing rectangle.
    d.line([(658,439),(628,347),(570,326)],'#a5aca4',32)
    d.line([(658,439),(628,347),(570,326)],CREAM,28)
    q=math.sin(t*1.8)*15
    d.line([(609,349),(552,301+q),(535,260+q)],'#a5aca4',22)
    d.line([(609,349),(552,301+q),(535,260+q)],CREAM,18)
    d.rr((524,244+q,547,281+q),10,CREAM,'#b1b7ab',1)


def render_frame(episode,beat,index,local,progress,width=1280,height=720):
    accent=episode.get('accent','#62a39b');secondary=episode.get('secondary','#cda76b')
    scene=beat.get('scene','desk');t=float(local);p=max(0,min(1,float(progress)))
    kind=scene if scene in ('stage','street','bench','door') else 'room'
    im=background(accent,secondary,kind,width,height).copy();d=D(im)
    mood='focused' if p>.54 else 'tired'
    # Native-resolution drawings, with shot changes at action boundaries.
    if scene in ('desk','write','send','organize'):
        window(d,t=t);clock(d,t=t*.1,accent=accent);plant(d,856,418,.9)
        desk_set(d,t,accent,secondary,scene in ('write','send'))
        character(d,375,320,t,'type' if scene in ('write','send') else 'sit',accent,mood=mood)
        if scene=='send':
            d.rr((542,267,646,289),4,accent);d.text((565,271),'SENT' if t>3 else 'SEND',12,'#eff3e5',True)
        if scene=='organize':
            for j in range(4):d.line([(712+j*7,314),(715+j*7,281)],blend(accent,secondary,j/4),3)
            d.rr((727,297,747,316),3,'#636a62')
        if (index%3==1 and t>3.4) or (scene in ('write','send') and t>6.5):
            # A finite cut to the object after the action, not constant zoom.
            crop=(460,190,720,330) if t>6.5 else (299,193,738,432)
            sx=width/960;box=tuple(round(a*sx) for a in crop)
            detail=im.crop(box).resize((width,round(height*.77)),Image.Resampling.LANCZOS)
            im.paste(detail,(0,round(height*.05)));d=D(im)
    elif scene=='phone':
        if index%2==0:phone_macro(d,t,accent,secondary,index)
        else:
            window(d,t=t);d.rr((265,277,655,416),26,'#303744','#687b87',2)
            for x in (280,640):d.line([(x,412),(x,428)],'#8c9698',3)
            d.rr((277,293,643,369),15,'#242f3c')
            character(d,450,324,t,'phone',accent,mood=mood);plant(d,760,416,1.0)
    elif scene=='clock':
        clock(d,480,245,137,t,accent)
        d.center('TIME KEEPS MOVING',412,17,'#95a7a8')
    elif scene in ('window','rain'):
        window(d,565,81,254,244,t,scene=='rain' or index%3==0)
        d.rr((539,328,847,340),3,'#4a5969','#71808b',1)
        character(d,371,318,t,'stand',accent,mood=mood)
        if scene=='rain':
            for j in range(34):
                x=(j*97+t*37)%960;y=75+(j*57+t*139)%339
                d.line([(x,y),(x-5,y+14)],'#374e60',1)
    elif scene=='bed':
        window(d,t=t);clock(d,208,303,24,t,accent)
        d.rr((150,334,243,420),10,'#38424a','#727d7d',2)
        d.rr((280,345,704,418),17,'#364450','#7d8c94',2)
        d.ellipse((303,316,369,374),CREAM,'#a2aea8',2)
        d.line([(318,342),(328,342)],'#49534f',2);d.line([(342,342),(352,342)],'#49534f',2)
        d.rr((365,339,695,400),15,blend(accent,'#26303c',.78),'#708087',2)
        for j in range(3):d.line([(404+j*64,350),(426+j*64,362),(450+j*64,358)],'#53626e',1)
    elif scene=='notes':
        d.poly([(307,95),(670,108),(650,424),(288,409)],'#d9d2bd','#8c928a',2)
        d.line([(342,110),(323,405)],blend(secondary,'#c96553',.35),2)
        for j in range(10):d.line([(344,150+j*23),(630,163+j*23)],'#b5b9aa',1)
        label={'01':'BE HERE.','02':'PRINT NO. 1','03':'TONIGHT','04':'BUILD DAY','05':'OUR STREET','06':'TRY AGAIN','07':'PLAY AGAIN','08':'ENOUGH FOR TODAY','09':'SAY HELLO','10':'ONE SONG'}.get(str(episode.get('id','')),'NEXT STEP')
        d.text((362,124),label,18,'#41535a',True)
        for j in range(min(6,int(t/.9)+1)):
            d.line([(356,186+j*25),(402+((j*37+int(t*9))%196),190+j*25)],'#66746b',2)
        xx=441+math.sin(t*2)*75;yy=280+min(3,int(t/1.5))*24
        d.line([(xx,yy),(xx+86,yy+81)],'#92a59d',10)
        d.line([(xx,yy),(xx+86,yy+81)],accent,7)
        d.poly([(xx-7,yy-7),(xx+5,yy-2),(xx-2,yy+5)],'#574d3d')
    elif scene=='mirror':
        d.ellipse((545,92,772,422),'#162631','#70858e',5)
        d.ellipse((557,104,760,410),'#1b2d38','#455b67',2)
        character(d,657,315,t,'stand',blend(accent,'#7997a1',.4),.88,'sad',-1)
        character(d,353,321,t,'handhead' if p<.5 else 'stand',accent,1.0,mood)
        d.line([(566,151),(586,129)],'#9eafb1',2);d.line([(566,166),(597,130)],'#647e89',1)
    elif scene in ('phoneaway','kitchen'):
        d.rect((152,299,665,324),'#736d5a','#918f7b',1)
        d.rr((157,325,658,419),4,'#283842','#60717a',1)
        for x in (321,493):d.line([(x,329),(x,416)],'#67777a',2)
        for x in (197,368,541):d.line([(x,348),(x+21,348)],'#a8b3a9',2)
        mug(d,258,297,accent,1.25)
        d.arc((401,229,444,273),180,360,'#99a69c',3)
        d.rr((387,256,442,295),9,'#738781','#a4b1a6',1)
        d.poly([(441,265),(457,267),(443,280)],'#8a9c94')
        px=560-ease(t/2)*91 if scene=='phoneaway' else 470
        d.rr((px,283,px+39,296),4,accent,'#a4bcb6',1)
        character(d,733,322,t,'reach' if t<3 else 'stand',accent,mood=mood)
    elif scene=='door':
        d.rr((594,83,779,422),7,'#786a4e','#ada07b',3)
        d.rect((604,92,767,418),blend(secondary,'#c8c3a1',.4))
        q=ease(t/3);right=750-q*86
        d.poly([(604,94),(right,115),(right,417),(604,417)],'#273641','#768791',2)
        d.ellipse((right-20,264,right-13,271),secondary)
        character(d,363+ease(t/5)*122,321,t,'walk' if t<5 else 'stand',accent,mood='focused')
    elif scene=='arcade':
        d.rr((463,129,769,335),12,'#26313c','#7c8b96',3)
        d.rect((476,143,756,315),'#10232c')
        for j in range(24):
            x=482+(j*79+t*17)%263;y=149+(j*31)%153;d.ellipse((x,y,x+2,y+2),'#c3cbbb')
        x=612+math.sin(t*1.5)*65;d.poly([(x,214),(x-13,239),(x,233),(x+13,239)],accent)
        for j in range(3):d.rr((512+j*76,169,550+j*76,180),3,secondary)
        d.line([(447,339),(788,339)],'#7e8c90',8)
        d.rr((314,259,386,401),18,'#273341','#6a7d89',2)
        character(d,386,318,t,'play',accent,mood=mood)
        d.rr((395,299,435,316),8,'#61757b','#94aaa7',1)
        for x in (404,425):d.ellipse((x,305,x+4,309),accent)
    elif scene in ('street','bench','train'):
        if scene=='train':
            d.rr((121,83,836,422),18,'#25323f','#6c818c',3)
            for j in range(3):
                x=150+j*226;window(d,x,110,192,140,t)
                d.rr((x-4,287,x+191,360),12,blend(accent,'#263442',.8),'#607b87',2)
                d.line([(x,363),(x,419)],'#748790',4)
            character(d,489,316,t,'sit',accent,mood=mood)
            d.line([(127,272),(831,272)],'#9aa9a7',3)
        else:
            for j in range(6):
                x=25+j*168;bh=60+(j*29)%110
                d.rect((x,220-bh,x+120,370),'#1b2735')
                for n in range(3):d.rect((x+15+n*31,232-bh,x+22+n*31,245-bh),'#465c62')
            for x in (182,802):
                d.line([(x,139),(x,417)],'#83938f',5)
                d.arc((x-27,116,x+27,159),178,358,'#83938f',4)
                d.rr((x-28,145,x+28,155),6,secondary)
                d.ellipse((x-9,150,x+9,157),'#e7d2a1')
            if scene=='bench':
                d.rr((312,285,665,342),9,'#41525a','#849491',2)
                d.line([(300,351),(678,351)],'#8c9184',12)
                for x in (324,651):d.line([(x,355),(x,416)],'#6e817e',5)
                character(d,399,316,t,'sit',accent,mood=mood)
                if p>.58:character(d,578,317,t+1,'sit',secondary,.94,'focused',-1)
                d.text((281,178),'BUS STOP',17,'#a3b6b5',True)
            else:
                d.line([(0,385),(960,385)],'#708281',2)
                for j in range(7):d.line([(j*155,403),(j*155+57,403)],'#adab8c',3)
                character(d,385+math.sin(t*.25)*80,319,t,'walk',accent,mood=mood)
    elif scene=='stairs':
        for j in range(6):
            x=250+j*80;y=409-j*43
            d.poly([(x,y),(x+80,y),(x+80,418),(x,418)],'#303f49','#6e8187',2)
            d.line([(x,y),(x+80,y)],blend(secondary,'#637a7c',.5),3)
        n=min(3,int(t/1.8));character(d,240+n*80,313-n*43,t,'walk',accent,.8,mood)
        d.line([(237,307),(707,77)],'#9baca3',5)
    elif scene=='workbench':
        d.rr((236,307,784,327),4,'#71634d','#b39c74',2)
        for x in (259,757):d.line([(x,329),(x,417)],'#756a57',9)
        eid=str(episode.get('id',''))
        if eid=='02':
            # Original printmaking workspace, not the birdhouse from the gaming story.
            d.poly([(495,218),(657,225),(645,302),(487,295)],'#ddd1b7','#9c8b72',2)
            d.ellipse((541,238,598,278),None,accent,2)
            for k in range(5):d.line([(516+k*21,241),(528+k*18,279)],'#67736a',1)
            d.line([(605,276),(672,286)],'#a2aea7',7)
            d.rr((595,262,624,285),5,'#6e5451','#b5957e',2)
        elif eid=='06':
            # Slatted wooden bench under construction.
            for k in range(3):d.rr((494,238+k*13,661,248+k*13),2,'#a38b64','#c2a87c',1)
            for x in (514,634):d.line([(x,278),(x-5,307)],'#9e8965',9)
            d.line([(518,291),(635,291)],'#7e735c',5)
        elif eid=='08':
            # Repairable lamp, with visible cord and disassembled shade.
            d.ellipse((530,292,617,307),'#8d7f66','#bba37b',2)
            d.line([(572,296),(572,226)],'#9c8b6d',6)
            d.poly([(544,208),(603,208),(624,249),(523,249)],blend(secondary,'#c8b081',.4),'#bda57d',2)
            d.line([(612,300),(643,290),(660,302),(689,295)],'#6f7e81',2)
            d.rr((681,288,700,302),3,'#8c9490')
        else:
            d.rr((512,218,612,307),5,'#a48b62','#c3b18a',2)
            d.poly([(504,222),(563,174),(622,222)],'#526d6b','#a7b2a0',2)
            d.ellipse((549,243,576,269),'#33474d','#c1aa7a',2)
        for j in range(4):d.line([(249+j*16,117),(249+j*16,192)],'#74857f',5)
        d.line([(686,293),(729,257)],'#b0b4a5',6);d.rect((717,245,740,268),'#6b7b7b')
        character(d,447,322,t,'reach',accent,mood=mood)
        plant(d,836,417,.8)
    elif scene=='water':
        d.ellipse((294,408,671,435),'#212b32')
        d.poly([(356,184),(604,184),(581,415),(378,415)],'#273a45','#9bafb0',3)
        fill=390-ease((t%7)/6)*149
        d.poly([(369,fill),(591,fill),(579,409),(380,409)],blend(accent,'#203945',.65))
        d.ellipse((369,fill-9,591,fill+9),blend(accent,'#a2c2b7',.5),'#93b5b4',2)
        d.ellipse((356,174,604,194),'#263d49','#b5c5bd',3)
        d.line([(367,208),(383,374)],'#9eb9b9',3)
        for j in range(4):d.arc((418-j*13,fill-7-j*3,541+j*13,fill+8+j*3),10,170,'#80adae',1)
    elif scene=='calendar':
        d.poly([(267,107),(697,114),(680,421),(276,416)],'#d2cfbb','#8e9b90',2)
        d.rect((271,111,694,164),blend(accent,'#394e54',.4))
        d.text((311,125),'COMING BACK',24,'#e7e7d3',True)
        for j in range(28):
            x=309+(j%7)*49;y=187+(j//7)*49
            d.rr((x,y,x+34,y+32),3,None,'#a2ac9d',1)
            if j<min(25,int(t*2.5)+1) and j not in (9,13):d.line([(x+5,y+17),(x+12,y+24),(x+29,y+7)],accent,3)
        d.line([(368,112),(368,97)],'#879c9d',5);d.line([(590,112),(590,97)],'#879c9d',5)
    elif scene=='projector':
        d.rr((362,103,812,338),7,'#ced4c7','#7a8e8e',3)
        d.line([(585,339),(585,419)],'#81918f',5)
        for j in range(3):
            x=391+j*132;d.rr((x,139,x+108,294),8,blend(accent,'#233943',.65),'#97b1ac',1)
            d.ellipse((x+30,164,x+78,211),'#bec6b6');d.line([(x+24,240),(x+84,240)],secondary,4)
        d.rr((159,322,277,362),8,'#4b6570','#a0b6b1',2)
        d.ellipse((244,328,273,355),secondary)
        d.line([(182,365),(182,417)],'#7e928f',4)
        character(d,353,322,t,'stand',accent,.82,mood)
    elif scene in ('stage','piano'):
        if scene=='stage':
            for j in range(6):
                x=49+j*17;d.rr((x,58,x+18,406),8,blend(secondary,'#34232f',.80+j*.015))
                x=799+j*17;d.rr((x,58,x+18,406),8,blend(secondary,'#34232f',.80+j*.015))
            d.ellipse((254,387,745,440),blend(secondary,'#26332e',.78))
            d.line([(0,431),(960,431)],'#8a8e7b',4)
            d.line([(635,177),(635,402)],'#8d9e9c',4)
            d.rr((622,157,651,193),10,'#a1aca3','#c1c7b4',1)
            character(d,477,316,t,'wave' if p>.6 else 'stand',accent,mood=mood)
            for j in range(9):d.ellipse((j*122-15,452,j*122+45,501),'#111822')
        else:
            d.poly([(204,223),(730,223),(777,330),(164,330)],'#27333d','#76888e',3)
            for j in range(21):
                x=183+j*27;d.rect((x,264,x+25,323),'#d9dccb','#687c7d',1)
                if j%7 not in (2,6):d.rect((x+18,263,x+32,294),'#25343d')
            for x in (207,724):d.line([(x,331),(x,419)],'#5b6d74',9)
            if t%3>1:
                j=int(t*3)%20;x=183+j*27;d.rect((x,299,x+25,323),accent)
            d.line([(319,419),(351,329),(416,305+math.sin(t*4)*3)],CREAM,19)
            d.line([(667,419),(630,329),(547,305+math.sin(t*5)*3)],CREAM,19)
    elif scene=='books':
        d.rr((194,96,486,418),6,'#27343f','#69818b',3)
        for shelf in range(3):
            yy=184+shelf*92;d.line([(199,yy),(481,yy)],'#879184',6)
            for j in range(10):
                x=207+j*26;hh=39+(j*13)%35
                d.rr((x,yy-hh,x+18,yy-4),2,blend(accent,secondary,(j%5)/5),'#94a79d',1)
                d.line([(x+4,yy-12),(x+14,yy-12)],'#b0bba9',1)
        character(d,618,324,t,'read',accent,mood=mood)
        d.rr((560,355,689,369),7,'#526773','#8eaaa6',2)
        d.line([(582,370),(582,419)],'#7c8e8b',4)
    elif scene=='shoes':
        for x in (324,520):
            d.line([(x+54,117),(x+45,302)],'#3d5060',54)
            d.rr((x,299,x+139,379),22,blend(accent,'#4e6469',.45),'#a5b2a9',3)
            d.rr((x-4,368,x+145,390),8,'#9ea99f','#b8c1ae',2)
            for j in range(5):d.line([(x+42,318+j*9),(x+87,319+j*9)],CREAM,3)
            if x==324:
                q=math.sin(t*2)*10;d.line([(x+62,339),(x+34-q,300),(x+9-q,293)],CREAM,3)
                d.arc((x+43,279,x+80,309),160,360,CREAM,3)
    elif scene=='sofa':
        d.rr((243,223,727,411),26,'#34414f','#71848f',2)
        d.rr((269,244,704,352),17,'#263641')
        d.line([(481,247),(481,350)],'#536a76',2)
        for x in (248,697):d.rr((x,290,x+32,399),12,'#3d505d','#7f9199',2)
        character(d,458,319,t,'phone' if p<.5 else 'sit',accent,mood=mood)
        mug(d,786,377,secondary);d.rr((751,378,836,388),3,'#6d6b59')
    elif scene=='diagram':
        diagrams=episode.get('diagrams') or [{'title':'THE PATTERN','nodes':['NOTICE','CHOOSE','ACT']}]
        diagram=diagrams[int(beat.get('graphic_id',0))%len(diagrams)]
        title=diagram.get('title','THE PATTERN');nodes=diagram.get('nodes',[])
        for n,txt in enumerate(fit_lines(title,28,820,2)):d.center(txt,99+n*35,28,CREAM,True)
        count=max(1,len(nodes));step=800/count;start=(960-step*count)/2
        for j,txt in enumerate(nodes):
            if t<j*1.1:continue
            cx=start+step*(j+.5);cy=273;rw=min(87,step*.44)
            d.ellipse((cx-rw,cy-57,cx+rw,cy+57),blend(accent,'#152631',.84),accent,2)
            for n,line in enumerate(fit_lines(txt,15,rw*1.7,3)):d.text((cx,cy-18+n*21),line,15,CREAM,True,'mt')
            if j:
                px=cx-step+rw+6;qx=cx-rw-6
                d.line([(px,cy),(qx,cy)],secondary,2)
                d.poly([(qx,cy),(qx-8,cy-5),(qx-8,cy+5)],secondary)
        d.center('A pattern in this story — not measured data.',395,14,'#91a7a8')
    else:
        title=episode.get('title','ONE SMALL ACTION')
        for n,line in enumerate(fit_lines(title,42,815,3)):d.center(line.upper(),145+n*53,42,CREAM if n==0 else accent,True)
        d.center('HARDSTART FILMS',365,19,'#9fb4ad',True)
    # The caller composites captions after this. Keep the strip unobstructed.
    d=D(im);d.rect((0,454,960,540),'#0c121a')
    d.line([(24,453),(936,453)],'#293844',1)
    d.text((26,22),'HARDSTART FILMS',12,'#a7b9b8',True)
    return im.convert('RGB')

if __name__=='__main__':
    from pathlib import Path
    import time
    demo={'id':'01','title':'Your Attention Is Being Sold','accent':'#6bb7bd','secondary':'#d4a36b','diagrams':[{'title':'THE ATTENTION LOOP','nodes':['A SIGNAL','REACH','SHORT RELIEF','REPEAT']},{'title':'A LITTLE DISTANCE','nodes':['NOTICE','MOVE THE PHONE','RETURN']} ]}
    sheet=Image.new('RGB',(1280*3,720*10));start=__import__('time').perf_counter()
    for i,scene in enumerate(SCENES):
        beat={'scene':scene,'graphic_id':0};frame=render_frame(demo,beat,i,4,.62)
        sheet.paste(frame,((i%3)*1280,(i//3)*720))
    out=Path(__file__).with_name('preview.png');sheet.resize((1920,3600),Image.Resampling.LANCZOS).save(out)
    print('Validated',len(SCENES),'scenes;',round(__import__('time').perf_counter()-start,2),'seconds;',out)
