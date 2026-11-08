const {chromium}=require('playwright');const {spawn}=require('child_process');
// node render.js out.mp4 [fps] [t0] [t1]
(async()=>{const out=process.argv[2],fps=+process.argv[3]||30,t0=+process.argv[4]||0,t1=+process.argv[5]||75;
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/scene.html');
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
const n=Math.round((t1-t0)*fps);for(let i=0;i<n;i++){await p.evaluate(t=>render(t),t0+i/fps);
 const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if(i%150==0)console.log('frame',i,'/',n)}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',out)})();
