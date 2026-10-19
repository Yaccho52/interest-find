/* ============================================================ */
/* 第一部分：页面状态、基础安全转义与步骤指示 */
let DATA;
const state={step:1,broad:null,branch:null,leaf:null,start:'',end:'',shown:12,sort:'recommended'};
const main=document.querySelector('#main');
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl=value=>{try{const u=new URL(value);return ['https:','http:'].includes(u.protocol)?u.href:'#';}catch{return '#';}};
const locationIcon='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>';
const calendarIcon='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="5" width="16" height="16" rx="3"/><path d="M8 3v5m8-5v5M4 11h16"/></svg>';
function progress(){return `<nav class="progress" aria-label="选择进度">${['发现兴趣','选个方向','再选偏好'].map((s,i)=>`${i?'<span class="progress-line"></span>':''}<span class="step ${state.step===i+1?'active':state.step>i+1?'done':''}" ${state.step===i+1?'aria-current="step"':''}><span class="step-num">${state.step>i+1?'✓':i+1}</span>${s}</span>`).join('')}</nav>`;}
function dateBox(compact=false){return `<section class="date-box ${compact?'compact':''}" aria-label="可选活动时间"><div class="date-title">${calendarIcon} 哪段时间有空？<span class="optional">选填</span></div><p>留空就看看全部匹配活动，包括往期记录。也可以只填写一个日期。</p><div class="date-fields"><label>开始日期<input id="start-date" type="date" value="${escapeHtml(state.start)}" aria-describedby="date-error"></label><span class="date-separator">—</span><label>结束日期<input id="end-date" type="date" value="${escapeHtml(state.end)}" aria-describedby="date-error"></label>${compact?'<button class="primary" id="apply-dates">应用时间</button>':''}<button class="text-button" id="clear-dates">清空日期</button></div><div id="date-error" class="date-error" role="alert"></div></section>`;}
function breadcrumb(){return `<div class="breadcrumb"><span>发现香港</span><span>／</span><span>${escapeHtml(state.broad.label)}</span>${state.branch?`<span>／</span><span>${escapeHtml(state.branch.label)}</span>`:''}</div>`;}
function moveTo(step){state.step=step;render();window.scrollTo({top:0,behavior:'smooth'});main.focus({preventScroll:true});}

/* ============================================================ */
/* 第二部分：三轮兴趣选择，无需注册或登录 */
function render(){
  if(state.step===4){renderResults();return;}
  if(state.step===1){
    main.innerHTML=`<div class="fade-in"><section class="hero"><span class="kicker">✧ 一座城市，很多种喜欢</span><h1>今天，想发现<em>什么？</em></h1><p>从一点兴趣出发，找到属于你的香港体验。<br>点选三步，让下一次出门更有意思。</p></section>${progress()}<div class="section-heading"><h2>先选一个大方向</h2><span>不必想太多，跟着兴趣走</span></div><section class="choice-grid" aria-label="兴趣大方向">${DATA.tree.map(b=>`<button class="choice" data-broad="${b.id}"><img class="choice-image" src="${b.image}" alt="${b.label}主题插画"><div class="choice-body"><div class="choice-title">${b.label}<span class="choice-arrow">↗</span></div><p class="choice-description">${b.description}</p><span class="count">${b.count.toLocaleString()} 条活动记录 · 点击发现</span></div></button>`).join('')}</section><p class="gentle-note">无需登录 &nbsp;·&nbsp; 日期自由选择 &nbsp;·&nbsp; 真实来源可查</p></div>`;
    main.querySelectorAll('[data-broad]').forEach(button=>button.addEventListener('click',()=>{state.broad=DATA.tree.find(b=>b.id===button.dataset.broad);state.branch=null;state.leaf=null;moveTo(2);}));
  }else if(state.step===2){
    main.innerHTML=`<div class="subhero fade-in"><button class="back" id="back">← 返回兴趣大方向</button>${breadcrumb()}${progress()}<div class="eyebrow">A LITTLE MORE YOU</div><h1 class="subheading">在${escapeHtml(state.broad.label)}里，<br>你更想体验哪一种？</h1><section class="option-grid" aria-label="活动方向">${state.broad.branches.map(b=>`<button class="option" data-branch="${b.id}"><div class="option-top"><strong>${b.label}</strong><b>↗</b></div><p>${b.description}</p><small>${b.count} 条活动记录</small></button>`).join('')}</section><p class="gentle-note">接下来再选一次偏好，就能查看推荐。</p></div>`;
    document.querySelector('#back').onclick=()=>moveTo(1);
    main.querySelectorAll('[data-branch]').forEach(button=>button.onclick=()=>{state.branch=state.broad.branches.find(b=>b.id===button.dataset.branch);state.leaf=null;moveTo(3);});
  }else{
    main.innerHTML=`<div class="subhero fade-in"><button class="back" id="back">← 返回活动方向</button>${breadcrumb()}${progress()}<div class="eyebrow">MAKE IT YOURS</div><h1 class="subheading">最后，选一个你喜欢的偏好。</h1><p class="selection-hint">可以先选日期，也可以留空。点击下方选项，即可查看推荐。</p>${dateBox()}<section class="option-grid" aria-label="具体兴趣偏好">${state.branch.leaves.map(l=>`<button class="option" data-leaf="${l.key}"><div class="option-top"><strong>${l.label}</strong><b>↗</b></div><p>${l.id==='all'?'不设更细的兴趣限制，自由发现。':'为这份兴趣，留一点时间。'}</p><small>${l.count} 条活动记录</small></button>`).join('')}</section></div>`;
    document.querySelector('#back').onclick=()=>moveTo(2);
    bindDates();
    main.querySelectorAll('[data-leaf]').forEach(button=>button.onclick=()=>{if(!readDates())return;state.leaf=state.branch.leaves.find(l=>l.key===button.dataset.leaf);state.shown=12;moveTo(4);});
  }
}

/* ============================================================ */
/* 第三部分：可选起止日期校验，区间两端均包含 */
function readDates(){
  const start=document.querySelector('#start-date').value,end=document.querySelector('#end-date').value;
  const invalid=start&&end&&start>end;
  document.querySelector('#date-error').textContent=invalid?'结束日期不能早于开始日期，请调整后再继续。':'';
  document.querySelector('#end-date').setAttribute('aria-invalid',String(Boolean(invalid)));
  if(invalid)return false;
  state.start=start;state.end=end;return true;
}
function bindDates(){
  document.querySelector('#clear-dates').onclick=()=>{state.start='';state.end='';if(state.step===4){state.shown=12;renderResults();}else{document.querySelector('#start-date').value='';document.querySelector('#end-date').value='';document.querySelector('#date-error').textContent='';document.querySelector('#end-date').setAttribute('aria-invalid','false');}};
  const apply=document.querySelector('#apply-dates');if(apply)apply.onclick=()=>{if(readDates()){state.shown=12;renderResults();}};
}
function filtered(){
  let records=DATA.rankings[state.leaf.key].map(i=>DATA.events[i]);
  // 未填写日期时不默认过滤历史活动，且不以 Top-5 限制结果数量。
  if(state.start||state.end)records=records.filter(e=>e.dates.some(d=>(!state.start||d>=state.start)&&(!state.end||d<=state.end)));
  if(state.sort==='date')records.sort((a,b)=>(a.dates.find(d=>(!state.start||d>=state.start)&&(!state.end||d<=state.end))||'9999').localeCompare(b.dates.find(d=>(!state.start||d>=state.start)&&(!state.end||d<=state.end))||'9999'));
  return records;
}
function displayDates(e){
  const dates=(state.start||state.end)?e.dates.filter(d=>(!state.start||d>=state.start)&&(!state.end||d<=state.end)):e.dates;
  if(!dates.length)return '日期待确认';
  const first=dates[0].replaceAll('-','.'),last=dates.at(-1).replaceAll('-','.');
  let label=dates.length===1?first:`${first} — ${last}（共 ${dates.length} 个活动日）`;
  // 时间字段可能含完整日期文字，另保留可展开说明，不能把日期范围误当成每日举办。
  return label;
}

/* ============================================================ */
/* 第四部分：横版图片活动卡、推荐排序和完整目录分页 */
function card(e){
  const source=e.source==='LCSD'?'康文署':e.source==='government_open_data'?'政府赛事目录':e.source==='official_website_extraction'?'香港足总':'赛事官方资料';
  const category=e.category==='esports'?'电子竞技':e.category==='football'?'足球赛事':state.broad.label;
  const time=(e.session_time?`<p class="session-time">${escapeHtml(e.session_time)}</p>`:'')+(e.date_text?`<details class="time-detail"><summary>查看具体场次</summary><p>${escapeHtml(e.date_text)}</p></details>`:'');
  return `<article class="event-card"><div class="event-image"><img src="${escapeHtml(e.image)}" alt="${escapeHtml(category)}主题插画" loading="lazy" width="900" height="480"><span class="event-tag">${escapeHtml(category)}</span><span class="image-label">${escapeHtml(e.image_kind)}</span></div><div class="event-body"><h3>${escapeHtml(e.title)}</h3><div class="meta-row">${locationIcon}<span>${escapeHtml(e.venue||'地点待公布')}</span></div><div class="meta-row">${calendarIcon}<span>${escapeHtml(displayDates(e))}</span></div>${time}<div class="event-bottom"><span>${source}</span>${safeUrl(e.url)!=='#'?`<a href="${escapeHtml(safeUrl(e.url))}" target="_blank" rel="noopener noreferrer">活动详情 ↗</a>`:'<span>详情待公布</span>'}</div></div></article>`;
}
function renderResults(){
  const all=filtered();
  const noDates=!state.start&&!state.end;
  main.innerHTML=`<div class="subhero fade-in"><button class="back" id="back">← 调整我的兴趣</button>${breadcrumb()}<div class="result-heading"><div><div class="eyebrow">FOUND FOR YOU</div><h1>把喜欢，变成下一站。</h1><p>${noDates?'未设置时间：列出当前兴趣下的全部活动，包含往期记录。':'已按活动举办日期筛选，区间包含开始与结束当天。'}</p><div class="chips"><span class="chip">${escapeHtml(state.broad.label)}</span><span class="chip">${escapeHtml(state.branch.label)}</span><span class="chip">${escapeHtml(state.leaf.label)}</span></div></div><label class="sort-label"><span class="sr-only">结果排序</span><select id="sort"><option value="recommended" ${state.sort==='recommended'?'selected':''}>推荐优先</option><option value="date" ${state.sort==='date'?'selected':''}>活动日期从早到晚</option></select></label></div>${dateBox(true)}<p class="banner-note">主题插画仅作配图 · 数据快照 ${DATA.snapshot} · 活动场次及余票以官方为准</p><p class="result-count" role="status">找到 <strong>${all.length}</strong> 条活动记录${all.length?`，当前展示 ${Math.min(state.shown,all.length)} 条`:''}</p><section class="result-grid" aria-label="推荐活动">${all.length?all.slice(0,state.shown).map(card).join(''):`<div class="empty"><div class="eyebrow">A DIFFERENT DAY, PERHAPS</div><h2>这段时间，还没有匹配的活动。</h2><p>可以清空日期看看全部记录，<br>或返回上一步，换一个兴趣方向。</p><button class="primary" id="empty-clear">清空日期，查看全部</button></div>`}</section>${all.length>state.shown?`<div class="load-wrap"><button class="load-more" id="load-more">再看看更多 · 还有 ${all.length-state.shown} 条 ↓</button></div>`:''}<p class="gentle-note">不急着做决定，喜欢的活动会让出门更值得。</p></div>`;
  document.querySelector('#back').onclick=()=>moveTo(3);
  bindDates();
  document.querySelector('#sort').onchange=e=>{state.sort=e.target.value;state.shown=12;renderResults();};
  const load=document.querySelector('#load-more');if(load)load.onclick=()=>{const scroll=window.scrollY;state.shown+=12;renderResults();window.scrollTo(0,scroll);document.querySelector('#load-more')?.focus({preventScroll:true});};
  const empty=document.querySelector('#empty-clear');if(empty)empty.onclick=()=>{state.start='';state.end='';renderResults();};
}

/* ============================================================ */
/* 第五部分：数据说明和加载失败恢复 */
const about=document.querySelector('#about');
document.querySelector('#about-button').onclick=document.querySelector('#footer-about').onclick=()=>about.showModal();
document.querySelector('.dialog-close').onclick=()=>about.close();
about.addEventListener('click',e=>{if(e.target===about)about.close();});
fetch('data.json').then(response=>{if(!response.ok)throw Error('data unavailable');return response.json();}).then(data=>{DATA=data;render();}).catch(()=>{main.innerHTML='<div class="empty"><h2>活动资料暂时未能载入</h2><p>请检查网络，稍后再试。</p><button class="primary" onclick="location.reload()">重新载入</button></div>';});
