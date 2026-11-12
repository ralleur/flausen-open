import { test, expect } from '@playwright/test';
const sizes = [[320,740],[390,844],[768,1024],[1366,768],[1536,1024]];
for(const [width,height] of sizes) test(`layout and destinations at ${width}x${height}`,async({page})=>{
 await page.setViewportSize({width,height});
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',msg=>{if(msg.type()==='error') errors.push(msg.text());});
 await page.goto('/');
 await expect(page.locator('body')).toHaveClass('enhanced');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const scene=page.locator(width<=700?'.phone':'.desktop');
 for(const [label,id] of [['Play','play'],['Everyday','everyday'],['The idea','idea']]){
  const link=scene.getByRole('link',{name:label,exact:true});
  await expect(link).toBeVisible();
  if(width<=700){const box=await link.boundingBox();expect(box!.width).toBeGreaterThanOrEqual(44);expect(box!.height).toBeGreaterThanOrEqual(44);}
  await link.click();await expect(page).toHaveURL(new RegExp(`#${id}$`));
  await expect(page.locator(`#${id}`)).toBeVisible();await expect(page.locator(`#${id}`)).toBeFocused();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.keyboard.press('Escape');await expect(page).toHaveURL(/#mobile$/);
  await expect(link).toBeFocused();
 }
 expect(errors).toEqual([]);
});
test('keyboard, direct links and browser history',async({page})=>{
 await page.goto('/');await page.keyboard.press('Tab');await expect(page.locator('.skip-link')).toBeFocused();
 await page.keyboard.press('Tab');await expect(page.locator('.desktop a[href="#play"]')).toBeFocused();
 await page.keyboard.press('Enter');await expect(page.locator('#play')).toBeFocused();
 await page.getByRole('link',{name:'The idea ↗'}).click();await expect(page.locator('#idea')).toBeFocused();
 await page.goBack();await expect(page.locator('#play')).toBeVisible();
 await page.goto('/#everyday');await expect(page.locator('#everyday')).toBeFocused();
 await page.keyboard.press('Escape');await expect(page).toHaveURL(/#mobile$/);
});
test('static fallback without JavaScript and failed wordmark asset',async({browser,page})=>{
 const ctx=await browser.newContext({javaScriptEnabled:false});const plain=await ctx.newPage();
 await plain.goto('http://127.0.0.1:5173/');
 for(const id of ['play','everyday','idea']) await expect(plain.locator(`#${id}`)).toBeVisible();
 await plain.locator('.desktop a[href="#idea"]').click();await expect(plain).toHaveURL(/#idea$/);
 await ctx.close();
 await page.route('**/brand/wordmark.svg',route=>route.abort());await page.goto('/');
 await expect(page.locator('.wordmark-fallback')).toBeVisible();
 await page.locator('.desktop a[href="#play"]').click();await expect(page.locator('#play')).toBeVisible();
});
test('drag suppresses navigation, cancellation clears and motion sleeps',async({page})=>{
 await page.setViewportSize({width:1536,height:1024});await page.goto('/');
 await page.mouse.move(740,495);await page.mouse.down();await page.mouse.move(810,520,{steps:8});await page.mouse.up();
 await expect(page).toHaveURL(/\/$/);
 await page.waitForTimeout(1400);
 const part=page.locator('.desktop [data-part="blue-object"]');
 await expect(part).toHaveAttribute('transform','rotate(0 486 157)');
 await page.mouse.move(740,495);await page.mouse.down();await page.mouse.move(790,510);
 await part.locator('a').dispatchEvent('pointercancel',{pointerId:1});await page.mouse.up();
 await expect(part).toHaveAttribute('transform','rotate(0 486 157)');
 await part.locator('a').dispatchEvent('pointerenter',{pointerType:'mouse'});
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 await expect(part).toHaveAttribute('transform','rotate(0 486 157)');
 await part.locator('a').dispatchEvent('pointerenter',{pointerType:'mouse'});
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});
 await expect(part).toHaveAttribute('transform','rotate(0 486 157)');
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'));});
 await part.locator('a').dispatchEvent('pointerenter',{pointerType:'mouse'});
 await page.waitForTimeout(1500);
 await expect(part).toHaveAttribute('transform','rotate(0 486 157)');
});
test('reduced motion is static, touch taps navigate and touch scrolling works',async({browser})=>{
 const ctx=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,reducedMotion:'reduce'});
 const page=await ctx.newPage();await page.goto('http://127.0.0.1:5173/');
 await page.locator('.phone').getByRole('link',{name:'Everyday',exact:true}).tap();await expect(page.locator('#everyday')).toBeVisible();
 await page.keyboard.press('Escape');await expect(page.locator('body')).toHaveClass('enhanced');
 await page.locator('.phone [role="button"]').focus();await page.keyboard.press('Enter');
 await expect(page.locator('.phone [data-part="brown-weight"]')).not.toHaveAttribute('transform',/rotate\((?!0 )/);
 const touch=await ctx.newCDPSession(page);
 await touch.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:100,y:600}]});
 for(let y=580;y>=400;y-=20) await touch.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:100,y}]});
 await touch.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await expect.poll(()=>page.evaluate(()=>scrollY)).toBeGreaterThan(0);
 await ctx.close();
});
test('200% equivalent layout and enlarged editorial text',async({page})=>{
 await page.setViewportSize({width:683,height:384});await page.goto('/#idea');
 await page.addStyleTag({content:'.body-copy,.note{font-size:200%}'});
 await expect(page.locator('#idea h2')).toBeVisible();await expect(page.locator('#idea .back')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
