import { chromium } from '@playwright/test';
const browser = await chromium.launch({executablePath:'C:/Users/ramuv/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe', headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
page.on('pageerror', error => console.log('ERROR',error.message));
await page.goto('http://127.0.0.1:5174/');
await page.evaluate(() => document.fonts.ready);
await page.evaluate(async () => {
  const finite = document.getAnimations().filter(animation => animation.effect?.getComputedTiming().iterations !== Infinity);
  await Promise.all(finite.map(animation => animation.finished.catch(() => {})));
});
await page.screenshot({path:'qa/screenshots/chat-desktop.png',fullPage:false,animations:'disabled'});
console.log(await page.locator('h1').innerText());
await browser.close();
