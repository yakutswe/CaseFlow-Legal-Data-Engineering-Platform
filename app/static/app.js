const $ = (id) => document.getElementById(id);
const fmt = (n) => new Intl.NumberFormat().format(Number(n || 0));
const dateFmt = (value) => value ? new Date(value).toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'}) : '—';

async function json(url){
  const r = await fetch(url);
  if(!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

async function loadHealth(){
  try{
    const h = await json('/health');
    $('service-status').textContent = 'Service online';
    document.querySelector('.status-dot').style.background = '#58b67d';
  }catch(e){
    $('service-status').textContent = 'Service unavailable';
    document.querySelector('.status-dot').style.background = '#b65b58';
  }
}

async function loadStats(){
  try{
    const s = await json('/dashboard/stats');
    $('metric-cases').textContent = fmt(s.cases);
    $('metric-courts').textContent = fmt(s.courts);
    $('metric-citations').textContent = fmt(s.citations);
    const failures = Number(s.failed_records || 0);
    $('metric-health').textContent = failures === 0 ? 'Healthy' : `${failures} flagged`;
    $('metric-health').className = failures === 0 ? 'good' : 'bad';
    $('metric-health-note').textContent = s.latest_job ? `${s.latest_job.source_name} · ${s.latest_job.status}` : 'No ingestion run yet';
  }catch(e){
    ['metric-cases','metric-courts','metric-citations','metric-health'].forEach(id => $(id).textContent = '—');
    $('metric-health-note').textContent = 'Database unavailable';
  }
}

function renderCases(cases){
  const body = $('cases-body');
  if(!cases.length){ body.innerHTML = '<tr><td colspan="3" class="empty">No matching cases.</td></tr>'; return; }
  body.innerHTML = cases.map(c => `<tr><td><strong>${escapeHtml(c.case_name)}</strong><span class="subtext">${escapeHtml(c.docket_number || 'No docket')} · ID ${c.id}</span></td><td>${escapeHtml(c.court || String(c.court_id || '—'))}</td><td>${dateFmt(c.decision_date)}</td></tr>`).join('');
}

async function loadCases(search=''){
  try{
    const url = search ? `/cases?limit=8&case_name=${encodeURIComponent(search)}` : '/dashboard/recent-cases?limit=8';
    const cases = await json(url);
    renderCases(cases);
  }catch(e){ $('cases-body').innerHTML='<tr><td colspan="3" class="empty">Could not load cases. Confirm PostgreSQL is running.</td></tr>'; }
}

async function loadCitations(){
  try{
    const items = await json('/dashboard/top-citations?limit=7');
    $('citations-list').innerHTML = items.length ? items.map(x => `<div class="citation-item"><div><strong>${escapeHtml(x.case_name)}</strong><span>${escapeHtml(x.citation)}</span></div><span class="count">${fmt(x.count)}</span></div>`).join('') : '<p class="empty">No extracted citations yet.</p>';
  }catch(e){ $('citations-list').innerHTML='<p class="empty">Citation data unavailable.</p>'; }
}

async function loadJobs(){
  try{
    const jobs = await json('/dashboard/ingestion-jobs?limit=5');
    $('jobs-list').innerHTML = jobs.length ? jobs.map(j => `<div class="job"><div class="job-head"><strong>${escapeHtml(j.source_name)}</strong><span>${dateFmt(j.started_at)} · ${escapeHtml(j.status)}</span></div><div class="job-metrics"><div><b>${fmt(j.fetched_count)}</b><small>Fetched</small></div><div><b>${fmt(j.created_count)}</b><small>Created</small></div><div><b>${fmt(j.updated_count)}</b><small>Updated</small></div><div><b>${fmt(j.duplicate_count)}</b><small>Duplicate</small></div><div><b class="${j.failed_count ? 'bad' : 'good'}">${fmt(j.failed_count)}</b><small>Failed</small></div></div></div>`).join('') : '<p class="empty">No ingestion jobs recorded yet.</p>';
  }catch(e){ $('jobs-list').innerHTML='<p class="empty">Ingestion history unavailable.</p>'; }
}

function escapeHtml(value){ return String(value ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }

$('search-form').addEventListener('submit', e => { e.preventDefault(); loadCases($('search').value.trim()); });
Promise.allSettled([loadHealth(),loadStats(),loadCases(),loadCitations(),loadJobs()]);
