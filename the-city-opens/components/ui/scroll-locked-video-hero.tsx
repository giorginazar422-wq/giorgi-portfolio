"use client"
import {useEffect,useRef,useState,type CSSProperties} from "react"

export interface MetroHeroProps {
 videoSrc?:string; title?:string; scrollHint?:string; tagline?:string;
 signature?:{name:string;url:string}|false; scrubDistance?:number;
 className?:string; style?:CSSProperties;
}
const DEFAULT_VIDEO="https://cdn.21st.dev/assets/mirror/21/21a77eac28eacbb7e142016eefeaa0b4a766619e51113629a3bc6df6af066c0f.mp4"
const DEFAULT_SIGNATURE={name:"guglielmogiannattasio.exe",url:"https://www.guglielmogiannattasio.it"}
const clamp=(n:number,a=0,b=1)=>Math.min(b,Math.max(a,n))
const center:CSSProperties={position:"absolute",inset:0,display:"grid",placeItems:"center",textAlign:"center",padding:"0 6%",pointerEvents:"none",willChange:"opacity,transform,filter"}
export default function MetroHero({videoSrc=DEFAULT_VIDEO,title="THE CITY OPENS",scrollHint="SCROLL",tagline="Every door in the city is already open.",signature=DEFAULT_SIGNATURE,scrubDistance=3200,className,style}:MetroHeroProps){
 const section=useRef<HTMLDivElement>(null),video=useRef<HTMLVideoElement>(null),heading=useRef<HTMLDivElement>(null),hint=useRef<HTMLDivElement>(null),payoff=useRef<HTMLDivElement>(null),bar=useRef<HTMLDivElement>(null),slider=useRef<HTMLInputElement>(null)
 const target=useRef(0),started=useRef(false)
 const [ready,setReady]=useState(false),[failed,setFailed]=useState(false)
 function update(n:number){target.current=clamp(n);if(target.current>.001)started.current=true}
 function prime(){const v=video.current;if(v&&v.readyState<2)v.play().then(()=>v.pause()).catch(()=>{})}
 useEffect(()=>{
  const s=section.current,v=video.current;if(!s||!v)return
  const reduced=window.matchMedia("(prefers-reduced-motion: reduce)").matches
  let progress=0,raf=0,touch:number|null=null
  target.current=0;started.current=false;setReady(false);setFailed(false)
  const distance=Math.max(1,scrubDistance)
  const oldOverflow=document.body.style.overflow,oldOverscroll=document.body.style.overscrollBehavior
  document.body.style.overflow="hidden";document.body.style.overscrollBehavior="none"
  const loaded=()=>{setReady(true);v.pause()},error=()=>setFailed(true)
  v.addEventListener("loadeddata",loaded);v.addEventListener("canplay",loaded);v.addEventListener("error",error)
  if(v.readyState>=2)loaded();else prime()
  const isControl=(t:EventTarget|null)=>t instanceof Element&&!!t.closest("button,input,a")
  const wheel=(e:WheelEvent)=>{if(e.ctrlKey||isControl(e.target)||reduced)return;e.preventDefault();update(target.current+e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?window.innerHeight:1)/distance);prime()}
  const start=(e:TouchEvent)=>{touch=isControl(e.target)||e.touches.length!==1?null:e.touches[0].clientY;prime()}
  const move=(e:TouchEvent)=>{if(touch===null||e.touches.length!==1||reduced)return;const y=e.touches[0].clientY;update(target.current+(touch-y)/distance);touch=y;if(e.cancelable)e.preventDefault()}
  const end=()=>{touch=null}
  const key=(e:KeyboardEvent)=>{if(isControl(e.target)||e.ctrlKey||e.metaKey||e.altKey)return;let n=target.current;if(["ArrowRight","ArrowDown","PageDown"," "].includes(e.key))n+=.06;else if(["ArrowLeft","ArrowUp","PageUp"].includes(e.key))n-=.06;else if(e.key==="Home")n=0;else if(e.key==="End")n=1;else return;e.preventDefault();update(n);prime()}
  s.addEventListener("wheel",wheel,{passive:false});s.addEventListener("touchstart",start,{passive:true});s.addEventListener("touchmove",move,{passive:false});s.addEventListener("touchend",end);s.addEventListener("touchcancel",end);window.addEventListener("keydown",key)
  function frame(){
   progress=reduced?target.current:progress+(target.current-progress)*.18;if(Math.abs(target.current-progress)<.0001)progress=target.current
   if(v&&Number.isFinite(v.duration)&&v.duration>0&&!v.seeking&&v.readyState>=1){const t=clamp(progress*v.duration,0,Math.max(0,v.duration-.015));if(Math.abs(v.currentTime-t)>.015)v.currentTime=t}
   if(v)v.style.transform=reduced?"none":`scale(${1+progress*.06})`
   const a=1-clamp(progress/.35),b=clamp((progress-.82)/.18)
   if(heading.current){heading.current.style.opacity=String(a);heading.current.style.transform=reduced?"none":`translateY(${(1-a)*-24}px) scale(${.96+a*.04})`;heading.current.style.filter=reduced?"none":`blur(${(1-a)*10}px)`}
   if(payoff.current){payoff.current.style.opacity=String(b);payoff.current.style.transform=reduced?"none":`translateY(${(1-b)*20}px) scale(${.97+b*.03})`;payoff.current.style.filter=reduced?"none":`blur(${(1-b)*8}px)`}
   if(hint.current)hint.current.style.opacity=started.current?"0":"1"
   if(bar.current)bar.current.style.transform=`scaleX(${progress})`
   if(slider.current&&document.activeElement!==slider.current)slider.current.value=String(Math.round(target.current*1000))
   raf=requestAnimationFrame(frame)
  }
  raf=requestAnimationFrame(frame)
  return()=>{cancelAnimationFrame(raf);v.pause();v.removeEventListener("loadeddata",loaded);v.removeEventListener("canplay",loaded);v.removeEventListener("error",error);s.removeEventListener("wheel",wheel);s.removeEventListener("touchstart",start);s.removeEventListener("touchmove",move);s.removeEventListener("touchend",end);s.removeEventListener("touchcancel",end);window.removeEventListener("keydown",key);document.body.style.overflow=oldOverflow;document.body.style.overscrollBehavior=oldOverscroll}
 },[videoSrc,scrubDistance])
 return <div ref={section} className={className} style={{position:"relative",height:"100dvh",width:"100%",overflow:"hidden",background:"#05070d",color:"#f2f4f8",touchAction:"none",fontFamily:"system-ui,sans-serif",...style}}>
 <video ref={video} src={videoSrc} muted playsInline preload="auto" style={{position:"absolute",inset:0,width:"100%",height:"100%",objectFit:"cover",opacity:ready?1:0,transition:"opacity .6s",pointerEvents:"none"}}/>
 <div style={{position:"absolute",inset:0,background:"linear-gradient(180deg,rgba(5,7,13,.35),transparent 30%,rgba(5,7,13,.15) 70%,rgba(5,7,13,.55))",pointerEvents:"none"}}/>
 <div ref={heading} style={center}><h1 style={{fontSize:"clamp(30px,7vw,96px)",fontWeight:800,letterSpacing:"-.02em",lineHeight:1,textShadow:"0 4px 30px #0008",margin:0}}>{title}</h1></div>
 {tagline&&<div ref={payoff} style={{...center,opacity:0,fontWeight:700,fontSize:"clamp(20px,3.4vw,40px)",textShadow:"0 4px 24px #0008"}}>{tagline}</div>}
 <div ref={hint} style={{position:"absolute",left:"50%",bottom:"clamp(64px,11vh,100px)",transform:"translateX(-50%)",display:"grid",justifyItems:"center",gap:8,letterSpacing:".3em",fontSize:12,transition:"opacity .4s",pointerEvents:"none"}}>{scrollHint}<svg width="14" height="18" viewBox="0 0 14 18" aria-hidden="true"><path d="M7 1L7 17M2 12L7 17L12 12" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg></div>
 {!ready&&<p role="status" style={{position:"absolute",top:20,left:"50%",transform:"translateX(-50%)",fontSize:12,textAlign:"center"}}>{failed?"Video could not load. Check your connection and refresh.":"Loading film…"}</p>}
 <div style={{position:"absolute",left:"50%",bottom:42,transform:"translateX(-50%)",display:"flex",gap:10,width:"min(270px,70vw)",alignItems:"center",touchAction:"auto"}}><button type="button" aria-label="Restart film" onClick={()=>{target.current=0;started.current=false;prime()}} style={{border:"1px solid #fff6",borderRadius:"50%",width:30,height:30,color:"white",background:"#05070d88",cursor:"pointer"}}>↺</button><input ref={slider} type="range" min={0} max={1000} defaultValue={0} aria-label="Film progress" onChange={e=>{update(Number(e.currentTarget.value)/1000);prime()}} style={{width:"100%",accentColor:"white"}}/></div>
 <div style={{position:"absolute",bottom:0,left:0,width:"100%",height:2,background:"#ffffff20"}}><div ref={bar} style={{height:"100%",background:"white",transform:"scaleX(0)",transformOrigin:"left"}}/></div>
 {signature&&<div style={{position:"absolute",right:"clamp(12px,2.5vw,24px)",bottom:15,color:"#dce0e899",fontSize:12}}>by <a href={signature.url} target="_blank" rel="noopener noreferrer" style={{color:"inherit",textDecoration:"none"}}>{signature.name}</a></div>}
 </div>
}
