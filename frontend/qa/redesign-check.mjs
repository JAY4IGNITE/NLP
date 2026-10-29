import { spawn } from 'node:child_process';
import { chromium, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

// Deterministic UI fixtures: this check never writes to the academic backend.
const departments = [{ id: 1, code: 'CSE', name: 'Computer Science & Engineering' }, { id: 2, code: 'IT', name: 'Information Technology' }];
const course = { id: 1, code: '241CS001', title: 'Programming fundamentals', department_code: 'CSE', category: 'MCC', credits: 3, lecture_hours: 3, tutorial_hours: 0, practical_hours: 0, total_hours: 3 };
const detail = { ...course, units: [{ unit_number: 1, unit_roman: 'I', title: 'Introduction', content: 'Problem solving and programming fundamentals.' }], outcomes: [{ outcome_code: 'CO1', description: 'Apply programming concepts.' }], textbooks: [{ book_type: 'textbook', title: 'Programming reference', raw_text: 'Programming reference' }] };
const report = { checks: [], layouts: [], accessibility: [], runtimeErrors: [], apiMode: 'Deterministic fixtures; no backend writes' };
const executablePath = process.env.CAMPUSAI_CHROMIUM || [join(process.env.LOCALAPPDATA || '', 'ms-playwright/chromium-1248/chrome-win64/chrome.exe'), 'C:/Users/ramuv/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe'].find(existsSync);
const server = spawn(process.execPath, ['node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5182', '--strictPort'], { windowsHide: true, stdio: 'pipe' });
let browser;
mkdirSync('qa/redesign', { recursive: true });
try {
  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Preview server did not start')), 15000);
    server.stdout.on('data', data => { if (data.toString().includes('Local:')) { clearTimeout(timeout); resolve(); } });
    server.on('error', reject);
    server.on('exit', code => { clearTimeout(timeout); reject(new Error(`Preview exited: ${code}`)); });
  });
  browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  page.on('pageerror', error => report.runtimeErrors.push(error.message));
  let submitted = [];
  await page.route('**/api/v1/**', async route => {
    const url = new URL(route.request().url());
    let data;
    if (url.pathname.endsWith('/departments')) data = departments;
    else if (url.pathname.endsWith('/courses/1')) data = detail;
    else if (url.pathname.endsWith('/courses')) data = url.searchParams.get('search')?.includes('missing') ? [] : [course];
    else if (url.pathname.endsWith('/semesters')) data = { department: 'Computer Science', department_code: url.searchParams.get('department_code'), semester_number: Number(url.searchParams.get('semester_number')), semester_roman: 'I', total_credits: 3, total_courses: 1, courses: [course] };
    else if (url.pathname.endsWith('/chat')) { submitted.push(route.request().postDataJSON()); data = { answer: 'This is a test response for the interface check.', session_id: 'ui-test', is_grounded: true }; }
    else data = {};
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(data) });
  });
  const base = 'http://127.0.0.1:5182';
  async function check(name, run) {
    try { await run(); report.checks.push({ name, passed: true }); console.log('PASS', name); }
    catch (error) { report.checks.push({ name, passed: false, error: error.message }); console.log('FAIL', name, error.message.slice(0, 300)); }
  }
  async function audit(name) {
    const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    report.accessibility.push({ name, violations: result.violations.map(v => ({ id: v.id, nodes: v.nodes.map(n => ({ target: n.target, summary: n.failureSummary })) })) });
  }
  async function navigate(name) {
    if (await page.getByRole('button', { name: 'Open navigation', exact: true }).isVisible()) await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
    await page.getByRole('navigation').getByRole('button', { name, exact: true }).click();
  }
  await page.goto(base);
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await check('Landing form sends exactly one question and opens usable chat', async () => {
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Your curriculum.Made clear.');
    await expect(page.getByRole('button', { name: 'Ask this question' })).toBeDisabled();
    await page.getByLabel('Your academic question').fill('Explain course credits');
    await page.getByRole('button', { name: 'Ask this question' }).click();
    await expect(page.getByText('This is a test response for the interface check.', { exact: true })).toBeVisible();
    expect(submitted).toHaveLength(1); expect(submitted[0].query).toBe('Explain course credits');
    expect((await page.getByLabel('Ask CampusAI', { exact: true }).boundingBox()).height).toBeGreaterThan(20);
    await navigate('Courses'); await navigate('Assistant');
    await expect(page.getByText('This is a test response for the interface check.', { exact: true })).toBeVisible();
  });
  await check('Landing links, browser history and direct routes', async () => {
    await page.getByRole('button', { name: 'CampusAI Home' }).click();
    await page.getByRole('button', { name: 'Explore courses', exact: true }).click();
    await expect(page).toHaveURL(/#explore$/); await page.goBack();
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Your curriculum.');
    await page.getByRole('button', { name: 'View semester plans' }).click();
    await expect(page).toHaveURL(/#semesters$/); await page.reload();
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Your semester');
  });
  await check('Catalog search, empty state and course details', async () => {
    await navigate('Courses');
    await page.getByRole('button', { name: course.title, exact: true }).click();
    await expect(page.getByRole('dialog', { name: 'Course details' })).toBeVisible();
    await audit('course-dialog-dark');
    await page.getByRole('button', { name: /Course Outcomes/ }).click();
    await expect(page.getByText('Apply programming concepts.')).toBeVisible();
    await page.keyboard.press('Escape');
    await page.getByLabel('Search courses').fill('missing');
    await expect(page.getByText('No courses match your filter criteria')).toBeVisible();
  });
  await check('Semester selection and comparison controls', async () => {
    await navigate('Semesters'); await page.getByRole('button', { name: 'Sem IV Sem 4', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Sem IV Sem 4', exact: true })).toHaveAttribute('aria-pressed', 'true');
    await navigate('Compare'); await page.getByLabel('Comparison department').selectOption('CSE');
    await page.getByLabel('Comparison semester').selectOption('4');
    await expect(page.getByLabel('Comparison semester')).toHaveValue('4');
  });
  await check('Admin sign-in opens and returns keyboard focus', async () => {
    const trigger = page.getByRole('button', { name: 'Admin sign in' });
    await trigger.click(); await expect(page.getByRole('dialog')).toBeVisible();
    await audit('login-dialog-dark');
    await page.keyboard.press('Escape'); await expect(trigger).toBeFocused();
  });
  for (const theme of ['dark', 'light']) {
    if (theme === 'light') await page.getByRole('button', { name: 'Switch to light mode' }).click();
    for (const [width, height] of [[1440, 1000], [900, 800], [768, 1024], [390, 844], [320, 740]]) {
      await page.setViewportSize({ width, height });
      for (const tab of ['home', 'chat', 'explore', 'semesters', 'compare']) {
        await page.goto(`${base}/#${tab}`);
        await expect(page.locator('html')).toHaveAttribute('data-theme', theme);
        await page.evaluate(() => document.fonts.ready);
        if (tab === 'explore') await expect(page.getByRole('button', { name: course.title, exact: true })).toBeVisible();
        if (tab === 'semesters') await expect(page.getByRole('table')).toBeVisible();
        const layout = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth, input: document.querySelector('.chat-page:not([hidden]) textarea')?.getBoundingClientRect().toJSON() }));
        report.layouts.push({ theme, tab, ...layout });
        await check(`${theme} ${tab} fits ${width}px`, async () => {
          expect(layout.scrollWidth).toBeLessThanOrEqual(width);
          if (layout.input) { expect(layout.input.height).toBeGreaterThan(20); expect(layout.input.bottom).toBeLessThanOrEqual(height); }
        });
        if (width === 1440 || width === 390) {
          await audit(`${tab}-${theme}-${width}`);
          await page.screenshot({ path: `qa/redesign/${tab}-${theme}-${width}.png`, fullPage: tab === 'home', animations: 'disabled' });
        }
      }
    }
  }
  await check('Mobile navigation exposes all destinations and closes after selection', async () => {
    await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
    await expect(page.getByRole('navigation')).toBeVisible();
    await page.getByRole('navigation').getByRole('button', { name: 'Courses', exact: true }).click();
    await expect(page.getByRole('navigation')).toBeHidden();
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Course catalog');
  });
  console.log('Accessibility violations:', report.accessibility.filter(a => a.violations.length).map(a => a.name).join(', ') || 'none');
  expect(report.runtimeErrors).toEqual([]);
} finally {
  writeFileSync('qa/redesign/report.json', JSON.stringify(report, null, 2));
  await browser?.close(); server.kill();
}
if (report.checks.some(c => !c.passed) || report.accessibility.some(a => a.violations.length) || report.runtimeErrors.length) process.exitCode = 1;
