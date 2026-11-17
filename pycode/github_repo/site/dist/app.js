/* ============================================================ */
/* 第一部分：语言、页面状态与基础安全转义 */
let DATA;
const LANG_STORAGE = 'hk-lang';
const readStored = () => { try { return localStorage.getItem(LANG_STORAGE); } catch { return null; } };
const writeStored = (value) => { try { localStorage.setItem(LANG_STORAGE, value); } catch { /* storage may be blocked */ } };
let LANG = (() => {
  const query = new URLSearchParams(location.search).get('lang');
  if (query === 'en' || query === 'zh') writeStored(query);
  return readStored() === 'en' ? 'en' : 'zh';
})();

const EN_NODES = {
  arts: { label: 'Culture & arts', desc: 'A show, an exhibition, or a bit of inspiration.' },
  sports: { label: 'Sports', desc: 'Go live and cheer for your team.' },
  esports: { label: 'Esports', desc: "From Summoner's Rift to the Counter-Strike stage." },
  music: { label: 'Live music', desc: 'Classical, pop and voices' },
  stage: { label: 'Theatre & dance', desc: 'Step into another world on stage' },
  art: { label: 'Exhibitions & workshops', desc: 'Look closely, try it yourself' },
  film: { label: 'Film & video', desc: 'Give the time to a good story' },
  family: { label: 'Family & reading', desc: 'A little curiosity for every age' },
  festival: { label: 'Festivals & more', desc: 'Stumble on a surprise in the city' },
  football: { label: 'Football', desc: 'HK Premier League and international football' },
  major: { label: 'More big events', desc: 'Tennis, rugby, volleyball and more' },
  cs2: { label: 'Counter-Strike 2', desc: 'BLAST Hong Kong, live on stage' },
  lol: { label: 'League of Legends', desc: 'LCK live in Hong Kong' },
  all: { label: 'All related events' },
  classical: { label: 'Classical & instrumental' },
  pop: { label: 'Pop music' },
  choir: { label: 'Choir & vocals' },
  dance: { label: 'Dance' },
  opera: { label: 'Chinese opera' },
  theatre: { label: 'Theatre' },
  multi: { label: 'Cross-media & variety' },
  exhibition: { label: 'Exhibitions' },
  workshop: { label: 'Workshops' },
  cinema: { label: 'Film screenings' },
  children: { label: 'Children' },
  reading: { label: 'Reading & literature' },
  festivals: { label: 'Festival programmes' },
  free: { label: 'Free entertainment' },
  hkpl: { label: 'HK Premier League' },
  international: { label: 'International football' },
  tennis: { label: 'Tennis' },
  rugby: { label: 'Rugby' },
  volleyball: { label: 'Volleyball' },
  golf: { label: 'Golf' },
  running: { label: 'Marathon' },
  other: { label: 'Other sports' },
  blast: { label: 'BLAST Hong Kong' },
  lck: { label: 'LCK Hong Kong' },
};

const S = {
  zh: {
    progress: ['发现兴趣', '选个方向', '再选偏好'],
    backDirections: '← 返回兴趣大方向',
    backOptions: '← 返回活动方向',
    backAdjust: '← 调整我的兴趣',
    kicker: '✧ 一座城市，很多种喜欢',
    heroTitle: '今天，想发现<em>什么？</em>',
    heroLead: '从一点兴趣出发，找到属于你的香港体验。<br>点选三步，让下一次出门更有意思。',
    directionTitle: '先选一个大方向',
    directionHint: '不必想太多，跟着兴趣走',
    countChoice: (n) => `${n.toLocaleString()} 条活动记录 · 点击发现`,
    note1: '无需登录 &nbsp;·&nbsp; 日期自由选择 &nbsp;·&nbsp; 真实来源可查',
    step2Title: (label) => `在${label}里，<br>你更想体验哪一种？`,
    step2Note: '接下来再选一次偏好，就能查看推荐。',
    step3Title: '最后，选一个你喜欢的偏好。',
    step3Hint: '可以先选日期，也可以留空。点击下方选项，即可查看推荐。',
    leafAll: '不设更细的兴趣限制，自由发现。',
    leafOther: '为这份兴趣，留一点时间。',
    countSmall: (n) => `${n} 条活动记录`,
    dateTitle: '哪段时间有空？',
    optional: '选填',
    dateHelp: '留空就看看全部匹配活动，包括往期记录。也可以只填写一个日期。',
    startDate: '开始日期',
    endDate: '结束日期',
    applyDates: '应用时间',
    clearDates: '清空日期',
    dateError: '结束日期不能早于开始日期，请调整后再继续。',
    crumbHome: '发现香港',
    resultsTitle: '把喜欢，变成下一站。',
    resultsNoDates: '未设置时间：列出当前兴趣下的全部活动，包含往期记录。',
    resultsDates: '已按活动举办日期筛选，区间包含开始与结束当天。',
    sortLabel: '结果排序',
    sortRecommended: '推荐优先',
    sortDate: '活动日期从早到晚',
    banner: (snapshot) => `主题插画仅作配图 · 数据快照 ${snapshot} · 活动场次及余票以官方为准`,
    found: (n) => `找到 <strong>${n}</strong> 条活动记录`,
    showing: (n) => `，当前展示 ${n} 条`,
    emptyTitle: '这段时间，还没有匹配的活动。',
    emptyText: '可以清空日期看看全部记录，<br>或返回上一步，换一个兴趣方向。',
    emptyButton: '清空日期，查看全部',
    loadMore: (n) => `再看看更多 · 还有 ${n} 条 ↓`,
    noteEnd: '不急着做决定，喜欢的活动会让出门更值得。',
    venueUnknown: '地点待公布',
    detailsUnknown: '详情待公布',
    detailsLink: '活动详情 ↗',
    sessions: '查看具体场次',
    dateUnknown: '日期待确认',
    eventDays: (n) => `（共 ${n} 个活动日）`,
    imageAlt: (label) => `${label}主题插画`,
    imageLabel: '主题插画',
    sourceLcsd: '康文署',
    sourceGovernment: '政府赛事目录',
    sourceHkfa: '香港足总',
    sourceOfficial: '赛事官方资料',
    categoryEsports: '电子竞技',
    categoryFootball: '足球赛事',
    loadFailTitle: '活动资料暂时未能载入',
    loadFailText: '请检查网络，稍后再试。',
    reload: '重新载入',
    documentTitle: '拾趣香港 · 给生活一点新发现',
    languageButton: 'EN',
    languageAria: 'Switch to English',
  },
  en: {
    progress: ['Discover', 'Narrow down', 'Choose'],
    backDirections: '← Back to directions',
    backOptions: '← Back to options',
    backAdjust: '← Adjust my interests',
    kicker: '✧ One city, many ways to like it',
    heroTitle: 'What do you want to discover <em>today?</em>',
    heroLead: 'Start from an interest and find your Hong Kong experience.<br>Three taps to make the next outing count.',
    directionTitle: 'Start with a direction',
    directionHint: 'No need to overthink — follow your interest',
    countChoice: (n) => `${n.toLocaleString()} events · tap to explore`,
    note1: 'No sign-in &nbsp;·&nbsp; dates optional &nbsp;·&nbsp; sources shown',
    step2Title: (label) => `In ${label},<br>what would you like to try?`,
    step2Note: 'One more choice and you will see the recommendations.',
    step3Title: 'Finally, pick a preference.',
    step3Hint: 'Set a date range if you like, or leave it blank. Tap an option to see recommendations.',
    leafAll: 'No further narrowing — browse freely.',
    leafOther: 'Make a little time for this interest.',
    countSmall: (n) => `${n} events`,
    dateTitle: 'When are you free?',
    optional: 'optional',
    dateHelp: 'Leave it blank to see every matching event, including past ones. You can also fill just one date.',
    startDate: 'Start date',
    endDate: 'End date',
    applyDates: 'Apply dates',
    clearDates: 'Clear dates',
    dateError: 'The end date cannot be earlier than the start date.',
    crumbHome: 'Discover Hong Kong',
    resultsTitle: 'Turn what you like into the next stop.',
    resultsNoDates: 'No dates set: every event under this interest is listed, including past ones.',
    resultsDates: 'Filtered by event dates; the range includes both the start and end day.',
    sortLabel: 'Sort results',
    sortRecommended: 'Recommended first',
    sortDate: 'Date, earliest first',
    banner: (snapshot) => `Thematic illustrations · data snapshot ${snapshot} · check official pages for sessions and tickets`,
    found: (n) => `Found <strong>${n}</strong> events`,
    showing: (n) => `, showing ${n}`,
    emptyTitle: 'No matching events in this period.',
    emptyText: 'Clear the dates to see everything,<br>or go back and try another direction.',
    emptyButton: 'Clear dates, show all',
    loadMore: (n) => `Show more · ${n} left ↓`,
    noteEnd: 'No rush — the right event makes the outing worth it.',
    venueUnknown: 'Venue to be announced',
    detailsUnknown: 'Details to be announced',
    detailsLink: 'Event details ↗',
    sessions: 'View session details',
    dateUnknown: 'Date to be confirmed',
    eventDays: (n) => ` (${n} event days)`,
    imageAlt: (label) => `${label} thematic illustration`,
    imageLabel: 'Theme illustration',
    sourceLcsd: 'LCSD',
    sourceGovernment: 'Gov. event catalogue',
    sourceHkfa: 'HKFA',
    sourceOfficial: 'Official event source',
    categoryEsports: 'Esports',
    categoryFootball: 'Football',
    loadFailTitle: 'Event data could not be loaded',
    loadFailText: 'Check your connection and try again.',
    reload: 'Reload',
    documentTitle: 'Interest HK · A new way to find your city',
    languageButton: '中文',
    languageAria: '切换到中文',
  },
};

const t = (key) => S[LANG][key];
const nodeLabel = (node) => (LANG === 'en' && EN_NODES[node.id] ? EN_NODES[node.id].label : node.label);
const nodeDesc = (node) => (LANG === 'en' && EN_NODES[node.id] && EN_NODES[node.id].desc ? EN_NODES[node.id].desc : node.description);
const eventTitle = (event) => (LANG === 'en' && event.title_en ? event.title_en : event.title);

const state = { step: 1, broad: null, branch: null, leaf: null, start: '', end: '', shown: 12, sort: 'recommended' };
const main = document.querySelector('#main');
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const safeUrl = (value) => { try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) ? u.href : '#'; } catch { return '#'; } };
const locationIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>';
const calendarIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="5" width="16" height="16" rx="3"/><path d="M8 3v5m8-5v5M4 11h16"/></svg>';

/* ============================================================ */
/* 第二部分：语言切换与静态文案 */
function applyStatic() {
  document.querySelectorAll('[data-en]').forEach((element) => {
    if (!element.dataset.zh) element.dataset.zh = element.innerHTML;
    element.innerHTML = LANG === 'en' ? element.dataset.en : element.dataset.zh;
  });
}

function updateChrome() {
  document.documentElement.lang = LANG === 'en' ? 'en' : 'zh-CN';
  document.title = t('documentTitle');
  const button = document.querySelector('#lang-toggle');
  if (button) {
    button.textContent = t('languageButton');
    button.setAttribute('aria-label', t('languageAria'));
  }
  const modelHref = LANG === 'en' ? 'model-en.html' : 'model.html';
  document.querySelectorAll('#model-link, #dialog-model-link').forEach((link) => { link.href = modelHref; });
}

function setLanguage(next) {
  LANG = next === 'en' ? 'en' : 'zh';
  writeStored(LANG);
  const url = new URL(location.href);
  url.searchParams.set('lang', LANG);
  history.replaceState(null, '', url);
  applyStatic();
  updateChrome();
  if (DATA) render();
}

/* ============================================================ */
/* 第三部分：步骤指示、日期框与面包屑 */
function progress() {
  return `<nav class="progress" aria-label="${LANG === 'en' ? 'Progress' : '选择进度'}">${t('progress').map((label, index) => `${index ? '<span class="progress-line"></span>' : ''}<span class="step ${state.step === index + 1 ? 'active' : state.step > index + 1 ? 'done' : ''}" ${state.step === index + 1 ? 'aria-current="step"' : ''}><span class="step-num">${state.step > index + 1 ? '✓' : index + 1}</span>${label}</span>`).join('')}</nav>`;
}

function dateBox(compact = false) {
  return `<section class="date-box ${compact ? 'compact' : ''}" aria-label="${LANG === 'en' ? 'Optional event dates' : '可选活动时间'}"><div class="date-title">${calendarIcon} ${t('dateTitle')}<span class="optional">${t('optional')}</span></div><p>${t('dateHelp')}</p><div class="date-fields"><label>${t('startDate')}<input id="start-date" type="date" value="${escapeHtml(state.start)}" aria-describedby="date-error"></label><span class="date-separator">—</span><label>${t('endDate')}<input id="end-date" type="date" value="${escapeHtml(state.end)}" aria-describedby="date-error"></label>${compact ? `<button class="primary" id="apply-dates">${t('applyDates')}</button>` : ''}<button class="text-button" id="clear-dates">${t('clearDates')}</button></div><div id="date-error" class="date-error" role="alert"></div></section>`;
}

function breadcrumb() {
  return `<div class="breadcrumb"><span>${t('crumbHome')}</span><span>／</span><span>${escapeHtml(nodeLabel(state.broad))}</span>${state.branch ? `<span>／</span><span>${escapeHtml(nodeLabel(state.branch))}</span>` : ''}</div>`;
}

function moveTo(step) {
  state.step = step;
  render();
  window.scrollTo({ top: 0, behavior: 'smooth' });
  main.focus({ preventScroll: true });
}

/* ============================================================ */
/* 第四部分：三轮兴趣选择，无需注册或登录 */
function render() {
  if (state.step === 4) { renderResults(); return; }
  if (state.step === 1) {
    main.innerHTML = `<div class="fade-in"><section class="hero"><span class="kicker">${t('kicker')}</span><h1>${t('heroTitle')}</h1><p>${t('heroLead')}</p></section>${progress()}<div class="section-heading"><h2>${t('directionTitle')}</h2><span>${t('directionHint')}</span></div><section class="choice-grid" aria-label="${LANG === 'en' ? 'Directions' : '兴趣大方向'}">${DATA.tree.map((broad) => `<button class="choice" data-broad="${broad.id}"><img class="choice-image" src="${broad.image}" alt="${t('imageAlt')(nodeLabel(broad))}"><div class="choice-body"><div class="choice-title">${nodeLabel(broad)}<span class="choice-arrow">↗</span></div><p class="choice-description">${nodeDesc(broad)}</p><span class="count">${t('countChoice')(broad.count)}</span></div></button>`).join('')}</section><p class="gentle-note">${t('note1')}</p></div>`;
    main.querySelectorAll('[data-broad]').forEach((button) => button.addEventListener('click', () => {
      state.broad = DATA.tree.find((broad) => broad.id === button.dataset.broad);
      state.branch = null;
      state.leaf = null;
      moveTo(2);
    }));
  } else if (state.step === 2) {
    main.innerHTML = `<div class="subhero fade-in"><button class="back" id="back">${t('backDirections')}</button>${breadcrumb()}${progress()}<div class="eyebrow">A LITTLE MORE YOU</div><h1 class="subheading">${t('step2Title')(escapeHtml(nodeLabel(state.broad)))}</h1><section class="option-grid" aria-label="${LANG === 'en' ? 'Directions' : '活动方向'}">${state.broad.branches.map((branch) => `<button class="option" data-branch="${branch.id}"><div class="option-top"><strong>${nodeLabel(branch)}</strong><b>↗</b></div><p>${nodeDesc(branch)}</p><small>${t('countSmall')(branch.count)}</small></button>`).join('')}</section><p class="gentle-note">${t('step2Note')}</p></div>`;
    document.querySelector('#back').onclick = () => moveTo(1);
    main.querySelectorAll('[data-branch]').forEach((button) => button.onclick = () => {
      state.branch = state.broad.branches.find((branch) => branch.id === button.dataset.branch);
      state.leaf = null;
      moveTo(3);
    });
  } else {
    main.innerHTML = `<div class="subhero fade-in"><button class="back" id="back">${t('backOptions')}</button>${breadcrumb()}${progress()}<div class="eyebrow">MAKE IT YOURS</div><h1 class="subheading">${t('step3Title')}</h1><p class="selection-hint">${t('step3Hint')}</p>${dateBox()}<section class="option-grid" aria-label="${LANG === 'en' ? 'Preferences' : '具体兴趣偏好'}">${state.branch.leaves.map((leaf) => `<button class="option" data-leaf="${leaf.key}"><div class="option-top"><strong>${nodeLabel(leaf)}</strong><b>↗</b></div><p>${leaf.id === 'all' ? t('leafAll') : t('leafOther')}</p><small>${t('countSmall')(leaf.count)}</small></button>`).join('')}</section></div>`;
    document.querySelector('#back').onclick = () => moveTo(2);
    bindDates();
    main.querySelectorAll('[data-leaf]').forEach((button) => button.onclick = () => {
      if (!readDates()) return;
      state.leaf = state.branch.leaves.find((leaf) => leaf.key === button.dataset.leaf);
      state.shown = 12;
      moveTo(4);
    });
  }
}

/* ============================================================ */
/* 第五部分：可选起止日期校验，区间两端均包含 */
function readDates() {
  const start = document.querySelector('#start-date').value;
  const end = document.querySelector('#end-date').value;
  const invalid = start && end && start > end;
  document.querySelector('#date-error').textContent = invalid ? t('dateError') : '';
  document.querySelector('#end-date').setAttribute('aria-invalid', String(Boolean(invalid)));
  if (invalid) return false;
  state.start = start;
  state.end = end;
  return true;
}

function bindDates() {
  document.querySelector('#clear-dates').onclick = () => {
    state.start = '';
    state.end = '';
    if (state.step === 4) {
      state.shown = 12;
      renderResults();
    } else {
      document.querySelector('#start-date').value = '';
      document.querySelector('#end-date').value = '';
      document.querySelector('#date-error').textContent = '';
      document.querySelector('#end-date').setAttribute('aria-invalid', 'false');
    }
  };
  const apply = document.querySelector('#apply-dates');
  if (apply) apply.onclick = () => { if (readDates()) { state.shown = 12; renderResults(); } };
}

function filtered() {
  let records = DATA.rankings[state.leaf.key].map((index) => DATA.events[index]);
  if (state.start || state.end) records = records.filter((event) => event.dates.some((date) => (!state.start || date >= state.start) && (!state.end || date <= state.end)));
  if (state.sort === 'date') records.sort((a, b) => (a.dates.find((date) => (!state.start || date >= state.start) && (!state.end || date <= state.end)) || '9999').localeCompare(b.dates.find((date) => (!state.start || date >= state.start) && (!state.end || date <= state.end)) || '9999'));
  return records;
}

function displayDates(event) {
  const dates = (state.start || state.end) ? event.dates.filter((date) => (!state.start || date >= state.start) && (!state.end || date <= state.end)) : event.dates;
  if (!dates.length) return t('dateUnknown');
  const first = dates[0].replaceAll('-', '.');
  const last = dates.at(-1).replaceAll('-', '.');
  return dates.length === 1 ? first : `${first} — ${last}${t('eventDays')(dates.length)}`;
}

/* ============================================================ */
/* 第六部分：横版图片活动卡、推荐排序和完整目录分页 */
function card(event) {
  const source = event.source === 'LCSD' ? t('sourceLcsd')
    : event.source === 'government_open_data' ? t('sourceGovernment')
      : event.source === 'official_website_extraction' ? t('sourceHkfa') : t('sourceOfficial');
  const category = event.category === 'esports' ? t('categoryEsports')
    : event.category === 'football' ? t('categoryFootball') : nodeLabel(state.broad);
  const session = event.session_time ? `<p class="session-time">${escapeHtml(LANG === 'en' ? event.session_time.replace('（香港时间）', ' (HKT)') : event.session_time)}</p>` : '';
  const time = session + (event.date_text ? `<details class="time-detail"><summary>${t('sessions')}</summary><p>${escapeHtml(event.date_text)}</p></details>` : '');
  const imageLabel = LANG === 'en' ? t('imageLabel') : event.image_kind;
  return `<article class="event-card"><div class="event-image"><img src="${escapeHtml(event.image)}" alt="${escapeHtml(t('imageAlt')(category))}" loading="lazy" width="900" height="480"><span class="event-tag">${escapeHtml(category)}</span><span class="image-label">${escapeHtml(imageLabel)}</span></div><div class="event-body"><h3>${escapeHtml(eventTitle(event))}</h3><div class="meta-row">${locationIcon}<span>${escapeHtml(event.venue || t('venueUnknown'))}</span></div><div class="meta-row">${calendarIcon}<span>${escapeHtml(displayDates(event))}</span></div>${time}<div class="event-bottom"><span>${source}</span>${safeUrl(event.url) !== '#' ? `<a href="${escapeHtml(safeUrl(event.url))}" target="_blank" rel="noopener noreferrer">${t('detailsLink')}</a>` : `<span>${t('detailsUnknown')}</span>`}</div></div></article>`;
}

function renderResults() {
  const all = filtered();
  const noDates = !state.start && !state.end;
  main.innerHTML = `<div class="subhero fade-in"><button class="back" id="back">${t('backAdjust')}</button>${breadcrumb()}<div class="result-heading"><div><div class="eyebrow">FOUND FOR YOU</div><h1>${t('resultsTitle')}</h1><p>${noDates ? t('resultsNoDates') : t('resultsDates')}</p><div class="chips"><span class="chip">${escapeHtml(nodeLabel(state.broad))}</span><span class="chip">${escapeHtml(nodeLabel(state.branch))}</span><span class="chip">${escapeHtml(nodeLabel(state.leaf))}</span></div></div><label class="sort-label"><span class="sr-only">${t('sortLabel')}</span><select id="sort"><option value="recommended" ${state.sort === 'recommended' ? 'selected' : ''}>${t('sortRecommended')}</option><option value="date" ${state.sort === 'date' ? 'selected' : ''}>${t('sortDate')}</option></select></label></div>${dateBox(true)}<p class="banner-note">${t('banner')(DATA.snapshot)}</p><p class="result-count" role="status">${t('found')(all.length)}${all.length ? t('showing')(Math.min(state.shown, all.length)) : ''}</p><section class="result-grid" aria-label="${LANG === 'en' ? 'Recommended events' : '推荐活动'}">${all.length ? all.slice(0, state.shown).map(card).join('') : `<div class="empty"><div class="eyebrow">A DIFFERENT DAY, PERHAPS</div><h2>${t('emptyTitle')}</h2><p>${t('emptyText')}</p><button class="primary" id="empty-clear">${t('emptyButton')}</button></div>`}</section>${all.length > state.shown ? `<div class="load-wrap"><button class="load-more" id="load-more">${t('loadMore')(all.length - state.shown)}</button></div>` : ''}<p class="gentle-note">${t('noteEnd')}</p></div>`;
  document.querySelector('#back').onclick = () => moveTo(3);
  bindDates();
  document.querySelector('#sort').onchange = (event) => { state.sort = event.target.value; state.shown = 12; renderResults(); };
  const load = document.querySelector('#load-more');
  if (load) load.onclick = () => {
    const scroll = window.scrollY;
    state.shown += 12;
    renderResults();
    window.scrollTo(0, scroll);
    document.querySelector('#load-more')?.focus({ preventScroll: true });
  };
  const empty = document.querySelector('#empty-clear');
  if (empty) empty.onclick = () => { state.start = ''; state.end = ''; renderResults(); };
}

/* ============================================================ */
/* 第七部分：数据说明、语言切换与加载失败恢复 */
applyStatic();
updateChrome();
document.querySelector('#lang-toggle').addEventListener('click', () => setLanguage(LANG === 'en' ? 'zh' : 'en'));

const about = document.querySelector('#about');
document.querySelector('#about-button').onclick = document.querySelector('#footer-about').onclick = () => about.showModal();
document.querySelector('.dialog-close').onclick = () => about.close();
about.addEventListener('click', (event) => { if (event.target === about) about.close(); });

fetch('data.json').then((response) => { if (!response.ok) throw Error('data unavailable'); return response.json(); }).then((data) => { DATA = data; render(); }).catch(() => {
  main.innerHTML = `<div class="empty"><h2>${t('loadFailTitle')}</h2><p>${t('loadFailText')}</p><button class="primary" onclick="location.reload()">${t('reload')}</button></div>`;
});
