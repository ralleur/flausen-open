import { chromium } from '@playwright/test';
import { mkdirSync, existsSync } from 'node:fs';
mkdirSync('test-results',{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || (existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined)});
const page=await browser.newPage();
for(const [width,height] of [[1536,1024],[1366,768],[768,1024],[390,844],[320,740]]) {
 await page.setViewportSize({width,height});await page.goto('http://127.0.0.1:5173/');await page.waitForTimeout(100);await page.screenshot({path:`test-results/${width}.png`,fullPage:true});
}
await page.goto('http://127.0.0.1:5173/#idea');await page.waitForTimeout(100);await page.screenshot({path:'test-results/content-320.png'});
await page.setViewportSize({width:1536,height:1024});await page.goto('http://127.0.0.1:5173/');await page.keyboard.press('Tab');await page.keyboard.press('Tab');await page.screenshot({path:'test-results/keyboard.png'});
await page.emulateMedia({reducedMotion:'reduce'});await page.mouse.move(740,495);await page.screenshot({path:'test-results/reduced-motion.png'});
await page.setViewportSize({width:683,height:384});await page.goto('http://127.0.0.1:5173/#everyday');await page.waitForTimeout(100);await page.screenshot({path:'test-results/zoom-equivalent.png',fullPage:true});
await page.setViewportSize({width:640,height:300});await page.setContent(`<body style="background:#eceef0;padding:25px;font:14px monospace">${[16,24,32,64].map(size=>`<span style="display:inline-grid;gap:20px;margin-right:30px">${size}px<img src="http://127.0.0.1:5173/brand/${size<32?'flausen-icon-small.svg':'flausen-symbol.svg'}" width="${size}" height="${size}"></span>`).join('')}<p><img src="http://127.0.0.1:5173/brand/flausen-symbol-mono.svg" width="64" height="64"> One colour</p>`);await page.screenshot({path:'test-results/symbols.png'});
await browser.close();
