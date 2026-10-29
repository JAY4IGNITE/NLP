import { chromium, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const executablePath = process.env.CAMPUSAI_CHROMIUM || [
  join(process.env.LOCALAPPDATA || '', 'ms-playwright/chromium-1248/chrome-win64/chrome.exe'),
  join(process.env.LOCALAPPDATA || '', 'ms-playwright/chromium-1234/chrome-win64/chrome.exe'),
].find(existsSync);
const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();
const report = { checks: [], runtimeErrors: [], accessibility: [], layouts: [], limitations: [] };
page.on('pageerror', error => report.runtimeErrors.push(error.message));
mkdirSync('qa/screenshots', { recursive: true });
const base = process.env.CAMPUSAI_PREVIEW || 'http://127.0.0.1:5174';
async function check(name, run) {
  try { await run(); report.checks.push({ name, passed: true }); console.log('PASS', name); }
  catch (error) { report.checks.push({ name, passed: false, error: error.message.slice(0,700) }); console.log('FAIL', name, error.message.slice(0,350)); await page.keyboard.press('Escape'); await page.keyboard.press('Escape'); }
}
async function shot(name) {
  await page.evaluate(() => document.fonts.ready);
  await page.mouse.move(0,0);
  await page.evaluate(async () => {
    const finite = document.getAnimations().filter(animation => animation.effect?.getComputedTiming().iterations !== Infinity);
    await Promise.all(finite.map(animation => animation.finished.catch(() => {})));
  });
  await page.screenshot({path:`qa/screenshots/${name}.png`,fullPage:false,animations:'disabled'});
}
async function audit(name) {
  const result = await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  report.accessibility.push({name, violations:result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});
}
async function layout(name) {
  const result = await page.evaluate(() => ({width:innerWidth, scrollWidth:document.documentElement.scrollWidth,
    composer:document.querySelector('.chat-page:not([hidden]) .chat-composer')?.getBoundingClientRect().toJSON(),
    dock:document.querySelector('.floating-dock')?.getBoundingClientRect().toJSON()}));
  report.layouts.push({name,...result});
  expect(result.scrollWidth).toBeLessThanOrEqual(result.width);
  if(result.composer) expect(result.composer.bottom).toBeLessThan(result.dock.top);
}
async function nav(name) { await page.getByRole('navigation',{name:'Main navigation'}).getByRole('button',{name,exact:true}).click(); }
await page.goto(base);
await check('Chat welcome, fonts, real catalog connectivity', async()=> {
  await expect(page.getByRole('heading',{name:'Your curriculum, made conversational.'})).toBeVisible();
  await expect(page.getByText('Catalog connected',{exact:true})).toBeVisible();
  await shot('chat-desktop'); await layout('chat-desktop'); await audit('chat-desktop');
});
await check('Chat submission, department and language payload, feedback, retained conversation', async()=> {
  await page.getByRole('button',{name:'CSE',exact:true}).click();
  await page.getByLabel('Response language').selectOption('en');
  await page.getByLabel('Ask CampusAI').fill('How many credits does Operating Systems have in CSE?');
  const sent=page.waitForRequest(r=>r.url().endsWith('/chat')&&r.method()==='POST');
  await page.getByRole('button',{name:'Send message'}).click();
  const body=(await sent).postDataJSON();
  expect(body.department_code).toBe('CSE'); expect(body.language_preference).toBe('en');
  await expect(page.locator('.assistant-message')).toHaveCount(1,{timeout:90000});
  await expect(page.locator('.thinking-indicator')).toHaveCount(0,{timeout:90000});
  await shot('chat-answer-desktop');
  const response=page.waitForResponse(r=>r.url().endsWith('/chat/feedback'));
  await page.getByRole('button',{name:'Helpful and accurate'}).click();
  expect((await response).ok()).toBeTruthy();
  await expect(page.getByText('Thank you. Your feedback has been saved.')).toBeVisible();
  await nav('Explore'); await nav('Chat');
  await expect(page.locator('.assistant-message')).toHaveCount(1);
});
await check('Citation opens original document, view modes, Escape focus return', async()=> {
  await page.locator('.citation-link').first().click();
  await expect(page.getByRole('dialog',{name:'Source document viewer'})).toBeVisible();
  await expect(page.locator('.source-image')).toBeVisible({timeout:30000});
  await shot('source-desktop'); await audit('source-desktop');
  await page.getByRole('button',{name:'Fit width',exact:true}).click();
  await expect(page.locator('.source-image')).toHaveClass(/fit-width/);
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.locator('.citation-link').first()).toBeFocused();
});
await check('Clear conversation and return to welcome', async()=> {
  await page.getByRole('button',{name:/New conversation/}).click();
  await expect(page.locator('.chat-message')).toHaveCount(0);
  await expect(page.getByRole('heading',{name:'Your curriculum, made conversational.'})).toBeVisible();
});
await nav('Explore');
await check('Catalog loads real courses and filters title, code, department, category', async()=> {
  await expect(page.locator('.course-card').first()).toBeVisible({timeout:20000});
  await shot('explore-desktop'); await audit('explore-desktop');
  await page.getByLabel('Search courses').fill('Operating Systems');
  await expect(page.locator('.course-card').first()).toContainText('Operating Systems');
  await page.getByRole('button',{name:'CSE-DS',exact:true}).click();
  await expect(page.locator('.course-card').first()).toContainText('CSE-DS');
  const code=(await page.locator('.course-card .font-mono').first().innerText()).trim();
  await page.getByLabel('Search courses').fill(code);
  await expect(page.locator('.course-card').first()).toContainText(code);
  await page.getByRole('button',{name:'PC',exact:true}).click();
  await expect(page.getByRole('button',{name:'PC',exact:true})).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:'All Categories',exact:true}).click();
});
await check('Course modal tabs and nested original source dialog', async()=> {
  await page.getByLabel('Search courses').fill('Operating Systems');
  await expect(page.locator('.course-card h3 button').first()).toContainText('Operating Systems');
  await page.locator('.course-card h3 button').first().click();
  await expect(page.getByRole('dialog',{name:'Course details'})).toBeVisible();
  await expect(page.getByRole('dialog').getByRole('heading',{level:2})).not.toContainText('Loading');
  await shot('course-desktop'); await audit('course-desktop');
  await page.getByRole('button',{name:/Course Outcomes/}).click();
  await expect(page.getByRole('button',{name:/Course Outcomes/})).toHaveAttribute('aria-pressed','true');
  await shot('course-outcomes-desktop');
  await page.getByRole('button',{name:/Textbooks/}).click(); await shot('course-books-desktop');
  await page.getByRole('button',{name:/Source Page/}).click();
  await expect(page.getByRole('dialog',{name:'Source document viewer'})).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog',{name:'Course details'})).toBeVisible();
  await page.keyboard.press('Escape');
});
await check('Semester switching and real curriculum table', async()=> {
  await nav('Semesters'); await expect(page.getByRole('table')).toBeVisible({timeout:20000});
  await shot('semesters-desktop'); await audit('semesters-desktop');
  await page.getByRole('button',{name:'Semester IV',exact:true}).click();
  await expect(page.getByRole('button',{name:'Semester IV',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(page.getByRole('table')).toBeVisible();
  await page.getByRole('button',{name:/Source Page/}).click();
  await expect(page.getByRole('dialog',{name:'Source document viewer'})).toBeVisible();
  await page.keyboard.press('Escape');
});
await check('Compare departments, exact-code shared/unique sets and credit difference',async()=> {
  await nav('Compare'); await expect(page.locator('.comparison-column')).toHaveCount(2,{timeout:20000});
  await shot('compare-desktop'); await audit('compare-desktop');
  await page.getByLabel('Comparison semester').selectOption('4');
  await expect(page.locator('.comparison-column')).toHaveCount(2);
  const department=await page.getByLabel('Primary department').inputValue();
  await page.getByLabel('Comparison department').selectOption(department);
  await expect(page.locator('.comparison-summary')).toContainText('Credit difference: 0');
  await expect(page.locator('.comparison-summary')).toContainText('0 Courses');
});
await check('Login dialog focus, password visibility, real authentication',async()=> {
  await page.getByRole('button',{name:/Admin sign in/}).click();
  await shot('login-desktop'); await audit('login-desktop');
  await page.getByRole('button',{name:'Show password'}).click();
  await expect(page.getByLabel('Password',{exact:true})).toHaveAttribute('type','text');
  await page.getByRole('button',{name:'Hide password'}).click();
  await page.getByRole('button',{name:'Sign In as Administrator'}).click();
  await expect(page.getByRole('dialog')).toHaveCount(0,{timeout:15000});
  await expect(page.getByRole('navigation').getByRole('button',{name:'Admin',exact:true})).toBeVisible();
});
await check('Admin real registry, issues and evaluation data',async()=> {
  await nav('Admin'); await expect(page.getByText('Curriculum source registry')).toBeVisible();
  await expect(page.getByRole('button',{name:/Documents \([1-9]/})).toBeVisible({timeout:15000});
  await shot('admin-documents-desktop'); await audit('admin-documents-desktop');
  await page.getByRole('button',{name:/Extraction review/}).click();
  await expect(page.getByText('Loading extraction records…')).toHaveCount(0,{timeout:20000});
  await shot('admin-issues-desktop'); await audit('admin-issues-desktop');
  const resolve = page.getByRole('button',{name:'Resolve Conflict'}).first();
  if (await resolve.count()) {
    await resolve.click(); await page.getByLabel('Resolution notes').fill('UI regression verification');
    await page.getByRole('button',{name:'Accept',exact:true}).click();
    await expect(page.getByRole('dialog',{name:'Administrator sign in'})).toBeVisible();
    report.limitations.push('Existing auth mismatch reproduced: API login supplies access_token; resolution handler requires user.token. No issue was modified.');
    await page.keyboard.press('Escape');
    await page.getByRole('button',{name:'Cancel resolution'}).click();
  } else report.limitations.push('No resolution control was available. Live issue records use pending_review while the existing UI checks pending. Issue mutations were not exercised; the existing access_token versus user.token mismatch also remains.');
  await page.getByRole('button',{name:'Evaluation metrics'}).click();
  await expect(page.locator('.evaluation-grid')).toBeVisible();
  await expect(page.locator('.evaluation-grid')).not.toContainText('Unavailable');
  await shot('admin-metrics-desktop'); await audit('admin-metrics-desktop');
});
for (const [width,height] of [[1280,800],[768,1024],[390,844],[320,740]]) {
  await page.setViewportSize({width,height});
  for(const name of ['Chat','Explore','Semesters','Compare','Admin']) {
    await check(`${name} layout ${width}x${height}`,async()=>{
      await nav(name);
      if(name==='Explore') await expect(page.locator('.course-card').first()).toBeVisible();
      if(name==='Semesters') await expect(page.getByRole('table')).toBeVisible();
      if(name==='Compare') await expect(page.locator('.comparison-column')).toHaveCount(2);
      await layout(`${name}-${width}`); await shot(`${name.toLowerCase()}-${width}`);
      if(width===390) await audit(`${name}-mobile`);
    });
  }
}
await page.setViewportSize({width:390,height:844});
await nav('Explore');
await check('Mobile course dialog, nested source, keyboard containment', async()=>{
  await page.locator('.course-card h3 button').first().click();
  await expect(page.getByRole('dialog').getByRole('heading',{level:2})).not.toContainText('Loading');
  await shot('course-mobile');
  for(const key of ['Tab','Shift+Tab']) {
    for(let i=0;i<12;i++) {
      await page.keyboard.press(key);
      expect(await page.evaluate(()=>document.activeElement?.closest('dialog')!==null)).toBeTruthy();
    }
  }
  await page.getByRole('button',{name:/Source Page/}).click();
  await expect(page.locator('.source-image')).toBeVisible({timeout:30000});
  await shot('source-mobile');
  for(let i=0;i<8;i++) {
    await page.keyboard.press('Tab');
    expect(await page.evaluate(()=>document.activeElement?.closest('dialog')?.getAttribute('aria-label'))).toBe('Source document viewer');
  }
  await page.keyboard.press('Escape'); await page.keyboard.press('Escape');
});
await check('Reduced motion and mobile sign out/login',async()=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await nav('Chat');
  await expect(page.getByRole('button',{name:'Chat',exact:true})).toHaveAttribute('aria-current','page');
  await page.getByRole('button',{name:'Sign out'}).click();
  await expect(page.getByRole('navigation').getByRole('button',{name:'Admin',exact:true})).toHaveCount(0);
  await page.getByRole('button',{name:/Admin sign in/}).click();
  await shot('login-mobile'); await page.keyboard.press('Escape');
});
await check('Catalog empty and offline states',async()=>{
  await nav('Explore'); await page.getByLabel('Search courses').fill('unfindable_course_xyz_826');
  await expect(page.getByText('No courses match your criteria')).toBeVisible(); await shot('explore-empty');
  await page.route('**/api/v1/courses?**', route=>route.abort('connectionfailed'));
  await page.getByLabel('Search courses').fill('offline test');
  await expect(page.getByRole('alert')).toContainText('could not be loaded'); await shot('explore-error');
  await page.unroute('**/api/v1/courses?**');
});
await check('Source image failure and successful retry',async()=> {
  await page.emulateMedia({reducedMotion:'no-preference'});
  await nav('Explore'); await page.getByLabel('Search courses').fill('Operating Systems');
  await expect(page.locator('.course-card h3 button').first()).toContainText('Operating Systems');
  await page.locator('.course-card h3 button').first().click();
  await page.route('**/sources/**/page/**',route=>route.abort('connectionfailed'));
  await page.getByRole('button',{name:/Source Page/}).click();
  await expect(page.getByRole('alert')).toContainText('This source page is unavailable.');
  await shot('source-error-mobile');
  await page.unroute('**/sources/**/page/**');
  await page.getByRole('button',{name:'Retry page'}).click();
  await expect(page.locator('.source-image')).toBeVisible({timeout:30000});
  await page.keyboard.press('Escape'); await page.keyboard.press('Escape');
});
await check('Course fetch error is visible and dismissible',async()=> {
  await page.route('**/api/v1/courses/*',route=>route.abort('connectionfailed'));
  await page.locator('.course-card h3 button').first().click();
  await expect(page.getByRole('alert')).toContainText('could not be loaded');
  await shot('course-error-mobile');
  await page.keyboard.press('Escape'); await page.unroute('**/api/v1/courses/*');
});
await check('Login invalid credentials show an inline error',async()=> {
  await page.getByRole('button',{name:/Admin sign in/}).click();
  await page.getByLabel('Password',{exact:true}).fill('invalid-regression-test-value');
  await page.getByRole('button',{name:'Sign In as Administrator'}).click();
  await expect(page.getByRole('alert')).toContainText('Invalid credentials');
  await shot('login-error-mobile'); await page.keyboard.press('Escape');
});
await check('Dock spring magnification, keyboard traversal and reduced motion',async()=> {
  await page.setViewportSize({width:1280,height:800}); await nav('Chat');
  const dock=page.getByRole('navigation',{name:'Main navigation'});
  const explore=dock.getByRole('button',{name:'Explore',exact:true});
  await explore.hover();
  await expect.poll(async()=>explore.locator('.dock-icon').evaluate(el=>new DOMMatrix(getComputedStyle(el).transform).a)).toBeGreaterThan(1.2);
  await explore.focus(); await page.keyboard.press('ArrowRight');
  await expect(dock.getByRole('button',{name:'Semesters',exact:true})).toBeFocused();
  await page.emulateMedia({reducedMotion:'reduce'});
  await expect.poll(async()=>explore.locator('.dock-icon').evaluate(el=>new DOMMatrix(getComputedStyle(el).transform).a)).toBe(1);
});
await browser.close();
writeFileSync('qa/verification.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.checks.filter(c=>c.passed).length,failed:report.checks.filter(c=>!c.passed).length,runtimeErrors:report.runtimeErrors,accessibility:report.accessibility.map(a=>({name:a.name,violations:a.violations.map(v=>v.id)})),limitations:report.limitations},null,2));
process.exitCode=report.checks.some(c=>!c.passed)||report.runtimeErrors.length||report.accessibility.some(a=>a.violations.length)?1:0;
