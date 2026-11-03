"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const os=require("node:os");
const net=require("node:net");
const {spawn,execFileSync}=require("node:child_process");
const {chromium}=require("playwright");
const root=path.resolve(__dirname,"..");
const python=process.env.LOCATION_PYTHON||path.join(root,".venv","bin","python");
const evidence=process.env.LOCATION_EVIDENCE||path.join(os.tmpdir(),"goreecloud-location-ui-review");
const pass="synthetic browser acceptance test password";
async function portNumber(){
  return new Promise((resolve,reject)=>{
    const srv=net.createServer();
    srv.once("error",reject);
    srv.listen(0,"127.0.0.1",()=>{let p=srv.address().port;srv.close(()=>resolve(p));});
  });
}
async function waitServer(url,proc){
 for(let i=0;i<100;i++){
  if(proc.exitCode!==null)throw Error("Service exited: "+proc.exitCode);
  try{if((await fetch(url+"/api/health")).ok)return;}catch(_){}
  await new Promise(r=>setTimeout(r,120));
 }
 throw Error("Service readiness timeout");
}
async function run(){
 fs.mkdirSync(evidence,{recursive:true});
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),"gc-location-qa-"));
 const env={...process.env,GC_LOCATION_DB:path.join(dir,"synthetic.sqlite")};
 execFileSync(python,["-c",
  "from goreecloud_location.store import initialize,create_account,default_db_path; p=default_db_path(); initialize(p); create_account(p,'browseruser','synthetic browser acceptance test password')"],{env});
 const port=await portNumber(),url="http://127.0.0.1:"+port;
 const proc=spawn(python,["-m","goreecloud_location.cli","serve","--host","127.0.0.1","--port",String(port)],{env,stdio:"ignore"});
 let browser=null;
 try{
  await waitServer(url,proc);
  browser=await chromium.launch({headless:true});
  for(const v of [{name:"desktop",width:1440,height:900},{name:"tablet",width:820,height:1180},{name:"mobile",width:390,height:844}]){
   const ctx=await browser.newContext({viewport:{width:v.width,height:v.height},acceptDownloads:true});
   const page=await ctx.newPage(),errors=[],external=[];
   const nav=(name)=>page.locator((v.width<=680?".mobile-nav":".sidebar")+" [data-nav="+name+"]");
   page.on("pageerror",e=>errors.push(e.message));
   page.on("console",m=>{if(m.type()==="error")errors.push(m.text());});
   page.on("request",q=>{const u=q.url();if(!u.startsWith(url+"/")&&!u.startsWith("data:")&&!u.startsWith("blob:"))external.push(u);});
   await page.goto(url,{waitUntil:"networkidle"});
   assert.equal(await page.locator("#login-screen").isVisible(),true);
   await page.screenshot({path:path.join(evidence,v.name+"-login.png"),fullPage:true});
   await page.locator("#username").fill("browseruser");
   await page.locator("#password").fill(pass);
   await page.locator("#login-form button[type=submit]").click();
   await page.waitForFunction(()=>document.querySelector("#metric-points").textContent.trim()!=="—");
   assert.equal(await page.locator("#app-shell").isVisible(),true);
   await page.screenshot({path:path.join(evidence,v.name+"-overview-empty.png"),fullPage:true});
   await nav("settings").click();
   assert.equal(await page.locator("#view-settings").isVisible(),true);
   await page.locator("#retention-preview").click();
   await page.locator("#retention-summary").getByText("0 GPS points").waitFor();
   const old=await page.locator("html").getAttribute("data-theme");
   await page.locator("#theme-toggle").click();
   assert.notEqual(await page.locator("html").getAttribute("data-theme"),old);
   await page.screenshot({path:path.join(evidence,v.name+"-settings-light.png"),fullPage:true});
   await page.locator("#theme-toggle").click();
   await nav("devices").click();
   await page.locator("#device-name").fill("Synthetic "+v.name+" device");
   await page.locator("#device-form button[type=submit]").click();
   await page.locator("#secret-dialog").waitFor({state:"visible"});
   assert.ok((await page.locator("#device-secret").textContent()).length>32);
   await page.screenshot({path:path.join(evidence,v.name+"-device-dialog.png"),fullPage:true,mask:[page.locator("#device-secret")]});
   await page.locator("#close-secret").click();
   await nav("overview").click();
   await ctx.grantPermissions(["geolocation"],{origin:url});
   await ctx.setGeolocation({latitude:35.987,longitude:-83.915,accuracy:12});
   await page.locator("#capture-location").click();
   await page.waitForFunction(()=>Number(document.querySelector("#metric-points").textContent.replaceAll(",",""))>0);
   await page.screenshot({path:path.join(evidence,v.name+"-overview-tracked.png"),fullPage:true});
   await nav("history").click();
   assert.match(await page.locator("#history-table").innerText(),/Synthetic/);
   await page.screenshot({path:path.join(evidence,v.name+"-history.png"),fullPage:true});
   const geometry=await page.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:innerWidth}));
   assert.ok(geometry.width<=geometry.viewport+2,"Horizontal overflow "+v.name+" "+JSON.stringify(geometry));
   assert.deepEqual(errors,[],"Browser JS and console errors");
   assert.deepEqual(external,[],"Unexpected third-party HTTP requests");
   await page.locator(v.width<=680?"#mobile-logout":"#logout").click();
   await page.locator("#login-screen").waitFor({state:"visible"});
   assert.equal(await page.locator("#app-shell").isVisible(),false);
   console.log("PASS",v.name,geometry);
   await ctx.close();
  }
 }finally{
  if(browser)await browser.close();
  proc.kill("SIGTERM");
  fs.rmSync(dir,{recursive:true,force:true});
 }
 console.log("EVIDENCE",evidence);
}
run().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
