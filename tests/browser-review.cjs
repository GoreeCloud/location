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
  "from goreecloud_location.store import initialize,create_account,default_db_path; p=default_db_path(); initialize(p); [create_account(p,u,'synthetic browser acceptance test password') for u in ('browserdesktop','browsertablet','browsermobile')]"],{env});
 const port=await portNumber(),url="http://127.0.0.1:"+port;
 const proc=spawn(python,["-m","goreecloud_location.cli","serve","--host","127.0.0.1","--port",String(port)],{env,stdio:"ignore"});
 let browser=null;
 try{
  await waitServer(url,proc);
  browser=await chromium.launch({headless:true});
  for(const v of [{name:"desktop",width:1440,height:900},{name:"tablet",width:820,height:1180},{name:"mobile",width:390,height:844}]){
   const ctx=await browser.newContext({viewport:{width:v.width,height:v.height},acceptDownloads:true});
   const page=await ctx.newPage(),errors=[],external=[];
   const nav=(name)=>page.locator((v.width<=680?".mobile-nav":".sidebar")+" button[data-nav="+name+"]");
   page.on("pageerror",e=>errors.push(e.message));
   page.on("console",m=>{if(m.type()==="error")errors.push(m.text());});
   page.on("request",q=>{const u=q.url();if(!u.startsWith(url+"/")&&!u.startsWith("data:")&&!u.startsWith("blob:"))external.push(u);});
   if(v.name==="mobile") {
     // Inject a malformed setting to verify the browser still never reaches
     // an off-host tile endpoint, even if /api/config is compromised.
     const maliciousPath="/"+String.fromCharCode(92)+"external.invalid/{z}/{x}/{y}.png";
     await page.route("**/api/config",route=>route.fulfill({
       status:200,contentType:"application/json",
       body:JSON.stringify({tile_template:maliciousPath,self_hosted:true})
     }));
   }
   await page.goto(url,{waitUntil:"networkidle"});
   assert.equal(await page.locator("#login-screen").isVisible(),true);
   await page.screenshot({path:path.join(evidence,v.name+"-login.png"),fullPage:true});
   await page.locator("#username").fill("browser"+v.name);
   await page.locator("#password").fill(pass);
   await page.locator("#login-form button[type=submit]").click();
   await page.waitForFunction(()=>document.querySelector("#metric-points").textContent.trim()!=="—");
   assert.equal(await page.locator("#app-shell").isVisible(),true);
   await page.screenshot({path:path.join(evidence,v.name+"-overview-empty.png"),fullPage:true});
   await nav("settings").focus();
   await nav("settings").press("Enter");
   assert.equal(await page.locator("#view-settings").isVisible(),true);
   const cardBoxes=await page.locator("#view-settings .prose-card").evaluateAll(nodes=>
     nodes.map(node=>{const b=node.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width};}));
   assert.equal(cardBoxes.length,3,"Three settings panels must remain visible");
   if(v.width>=1191) {
     assert.ok(Math.abs(cardBoxes[0].y-cardBoxes[2].y)<=2,"Desktop settings panels should form one balanced row");
   } else if(v.width>680) {
     assert.ok(cardBoxes[2].width>cardBoxes[0].width*1.5,"Tablet final panel should span both columns");
   } else {
     assert.ok(cardBoxes[2].y>cardBoxes[1].y,"Phone settings panels should stack vertically");
   }
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
   const tokenDialog=page.getByRole("dialog",{name:"Device added successfully"});
   await tokenDialog.waitFor({state:"visible"});
   assert.equal(await tokenDialog.getAttribute("aria-describedby"),"secret-description");
   assert.ok((await page.locator("#device-secret").textContent()).length>32);
   await page.screenshot({path:path.join(evidence,v.name+"-device-dialog.png"),fullPage:true,mask:[page.locator("#device-secret")]});
   await page.locator("#close-secret").focus();
   await page.keyboard.press("Enter");
   await page.locator("#secret-dialog").waitFor({state:"hidden"});
   assert.equal(await page.locator("#device-secret").textContent(),"");
   await page.locator("#devices-list .tiny-action.danger").last().click();
   const eraseDialog=page.getByRole("dialog",{name:"Erase device history?"});
   await eraseDialog.waitFor({state:"visible"});
   assert.equal(await eraseDialog.getAttribute("aria-describedby"),"erase-description");
   await page.keyboard.press("Escape");
   await eraseDialog.waitFor({state:"hidden"});
   await nav("overview").click();
   await ctx.grantPermissions(["geolocation"],{origin:url});
   await ctx.setGeolocation({latitude:35.987,longitude:-83.915,accuracy:12});
   const baseline=Number((await page.locator("#metric-points").textContent()).replaceAll(",",""));
   await page.locator("#capture-location").click();
   await page.waitForFunction(previous=>Number(document.querySelector("#metric-points").textContent.replaceAll(",",""))>previous,baseline,{timeout:10000});
   await page.getByText("Location captured privately.").waitFor({state:"visible",timeout:10000});
   await page.screenshot({path:path.join(evidence,v.name+"-overview-tracked.png"),fullPage:true});
   await nav("history").click();
   assert.match(await page.locator("#history-table").innerText(),new RegExp("Synthetic "+v.name+" device"));
   await page.screenshot({path:path.join(evidence,v.name+"-history.png"),fullPage:true});
   const geometry=await page.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:innerWidth}));
   assert.ok(geometry.width<=geometry.viewport+2,"Horizontal overflow "+v.name+" "+JSON.stringify(geometry));
   assert.deepEqual(errors,[],"Browser JS and console errors");
   assert.deepEqual(external,[],"Unexpected third-party HTTP requests");
   const logoutButton=page.locator(v.width<=680?"#mobile-logout":"#logout");
   await logoutButton.focus();
   await logoutButton.press("Enter");
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
