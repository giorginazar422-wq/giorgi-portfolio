const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1800,height:1100}});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(300);await p.screenshot({path:process.argv[3]});await b.close()})();
