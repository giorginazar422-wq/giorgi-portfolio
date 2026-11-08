# Весь звук синтезируется кодом (numpy), чужих записей нет.
import numpy as np, wave
SR=44100;D=75;N=SR*D;rng=np.random.default_rng(7);t=np.arange(N)/SR
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR);y=np.zeros_like(x);s=0.0
    for i in range(len(x)): s=a*s+(1-a)*x[i];y[i]=s
    return y
def lp_fast(x,fc):  # одно-полюсный ФНЧ через scipy-free свёртку
    k=max(1,int(SR/fc/2));return np.convolve(x,np.ones(k)/k,'same')
def env(n,a,r):
    e=np.ones(n);aa=int(a*SR);rr=int(r*SR);e[:aa]=np.linspace(0,1,aa);e[-rr:]=np.linspace(1,0,rr);return e
def place(buf,sig,at,g=1):
    i=int(at*SR);j=min(N,i+len(sig));buf[i:j]+=sig[:j-i]*g
# фон: низкий гул + медленная модуляция
drone=(np.sin(2*np.pi*55*t)*.5+np.sin(2*np.pi*55.4*t)*.4+np.sin(2*np.pi*82.4*t)*.2)*(0.7+0.3*np.sin(2*np.pi*.08*t))
drone+=lp_fast(rng.standard_normal(N),300)*3
drone*=np.minimum(1,t/3)*np.minimum(1,(D-t)/2)
# дождь (сцены 1,2,4,5)
rain=rng.standard_normal(N);rain=rain-lp_fast(rain,1200);rain=lp_fast(rain,9000)
rg=np.interp(t,[0,3,23,24,37,38,50,58,60,72],[.25,.35,.35,.1,.1,.4,.45,.3,.1,0]);rain*=rg
# ветер (двор)
wind=lp_fast(rng.standard_normal(N),500)*8;wind*=np.interp(t,[36,40,50,58,62],[0,.8,1,.8,0])*(.6+.4*np.sin(2*np.pi*.15*t))
sfx=np.zeros(N)
# шаги
step=lp_fast(rng.standard_normal(int(.14*SR)),600)*np.exp(-np.linspace(0,9,int(.14*SR)))*6
for i,at in enumerate(np.arange(41.4,48.6,.62)):place(sfx,step,at,.9 if i%2 else .7)
# скрип двери
n=int(1.4*SR);tt=np.arange(n)/SR;f=300+120*np.sin(2*np.pi*3*tt)+200*tt
creak=np.sin(2*np.pi*np.cumsum(f)/SR)*.25*env(n,.2,.5)*(0.6+0.4*rng.random(n))
place(sfx,creak,39.8);place(sfx,creak*.6,12.0)
# вибрация телефона
n=int(.35*SR);tt=np.arange(n)/SR;buz=np.sin(2*np.pi*170*tt)*env(n,.02,.05)*.5
for at in np.arange(23.5,29,.8):place(sfx,buz,at)
# электрический щелчок мигающей лампы
click=rng.standard_normal(int(.03*SR))*np.exp(-np.linspace(0,8,int(.03*SR)))*.5
for at in (11.2,13.7,19.3,24.1,27.6,33.4):place(sfx,click,at)
# нарастающий гул перед огнями и тишина в конце
rise=np.sin(2*np.pi*(40+t*0)*t)*0;m=(t>64)&(t<71.5);rise=np.sin(2*np.pi*(60+8*(t-64))*t)*m*np.interp(t,[64,70,71.5],[0,.7,.2])
place(sfx,np.zeros(1),0)
def norm(x,pk):return x/np.max(np.abs(x))*pk
mix={'bed':norm(drone*.9+rain*.5+wind*.4,.5),'fx':norm(sfx+rise,.6)}
for k,v in mix.items():
    w=wave.open(f'audio/{k}.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((v*32767).astype('<i2').tobytes());w.close()
print('ok')
