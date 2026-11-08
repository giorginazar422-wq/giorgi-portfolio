# Временная озвучка: Piper TTS (голос ru irina, GPLv2). Каждая фраза синтезируется отдельно,
# по реальной длине фраз строится тайминг слов (timeline.json / art/timeline.js).
import sys,json,re,wave,subprocess,numpy as np
from piper import PiperVoice, SynthesisConfig
M=sys.argv[1]
exec(open('gen_timeline.py',encoding='utf8').read().split('KEY=')[0])  # берём P (план фраз)
KEY={"луна","камень","семьдесят","два","часа","тормозит","свет","вчера","сторож"}
v=PiperVoice.load(M,config_path=M+'.json');SR=v.config.sample_rate
cfg=SynthesisConfig(length_scale=1.12,noise_scale=0.6,noise_w_scale=0.7)
OUT=np.zeros(SR*75,dtype=np.float32);words=[];prev=0.0
for pi,(a,b,txt) in enumerate(P):
    say=txt.replace('«','').replace('»','').replace('—',',')
    chunks=[np.frombuffer(c.audio_int16_bytes,dtype=np.int16) for c in v.synthesize(say,cfg)]
    x=np.concatenate(chunks).astype(np.float32)/32768
    nz=np.where(np.abs(x)>0.02)[0];x=x[max(0,nz[0]-200):nz[-1]+800]
    d=len(x)/SR;st=max(a,prev+0.35);i=int(st*SR);OUT[i:i+len(x)]+=x[:len(OUT)-i];prev=st+d
    ws=txt.split();wt=[len(re.sub(r'\W','',w))+2 for w in ws];tot=sum(wt);t=st
    for w,k in zip(ws,wt):
        dd=d*k/tot;words.append(dict(w=w,s=round(t,3),e=round(t+dd*.92,3),p=pi,key=re.sub(r'[^\w]','',w.lower()) in KEY));t+=dd
    print(f'{pi:2d} {st:6.2f}-{prev:6.2f} (план {a}-{b})  {txt}')
w=wave.open('audio/voice_tts.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(OUT,-1,1)*32767).astype('<i2').tobytes());w.close()
json.dump(words,open('timeline.json','w'),ensure_ascii=False,indent=1)
open('art/timeline.js','w').write('const TL='+json.dumps(words,ensure_ascii=False)+';')
