'use strict';

// ═══════════════════════════════════════════════════════════════
//  Layer definitions — saturated scales, visible on light bg
// ═══════════════════════════════════════════════════════════════
const LAYERS = {
  ai_exposure: {
    label: 'AI Exposure',
    domain: [0, 10],
    fn: t => d3.interpolateRgbBasis(['#5B8ED4','#8B5BA8','#D4580A','#FF9933'])(t),
    lo: '0 — no exposure', hi: '10 — fully reshapeable',
    tip: d => `AI Exposure: ${d.ai_exposure}/10`,
  },
  automation_risk: {
    label: 'Automation Risk',
    domain: [0, 10],
    fn: t => d3.interpolateRgbBasis(['#2E8B4A','#7DC44E','#FFA020','#CC2200'])(t),
    lo: '0 — safe', hi: '10 — high displacement',
    tip: d => `Automation Risk: ${d.automation_risk}/10`,
  },
  median_wage: {
    label: 'Median Annual Wage',
    domain: [72000, 1100000],
    fn: t => d3.interpolateRgbBasis(['#FFB74D','#66BB6A','#2E7D32'])(t),
    lo: '₹72K / yr', hi: '₹11L / yr',
    tip: d => `Wage: ${fmtWage(d.median_wage)}`,
  },
  formalization_potential: {
    label: 'Formalization Potential',
    domain: [0, 10],
    fn: t => d3.interpolateRgbBasis(['#9E9E9E','#7986CB','#3949AB','#1A237E'])(t),
    lo: '0 — structural informal', hi: '10 — rapidly formalising',
    tip: d => `Formalization: ${d.formalization_potential}/10`,
  },
  gig_potential: {
    label: 'Gig / Platform Potential',
    domain: [0, 10],
    fn: t => d3.interpolateRgbBasis(['#BDBDBD','#FFCA28','#FB8C00','#E65100'])(t),
    lo: '0 — no gig path', hi: '10 — born-platform',
    tip: d => `Gig Potential: ${d.gig_potential}/10`,
  },
  growth_outlook: {
    label: 'Growth Outlook',
    categorical: true,
    colors: {
      'fast-growing': '#1A237E',
      'growing':      '#1B5E20',
      'stable':       '#E65100',
      'declining':    '#B71C1C',
    },
    tip: d => `Growth: ${d.growth_outlook}`,
  },
};

const GROWTH_ORDER = ['fast-growing','growing','stable','declining'];

const SCORES = [
  { key:'ai_exposure',            label:'AI Exposure',   color:'#3949AB' },
  { key:'automation_risk',        label:'Automation',    color:'#C62828' },
  { key:'formalization_potential',label:'Formal.',       color:'#1B5E20' },
  { key:'gig_potential',          label:'Gig',           color:'#E65100' },
];

// ═══════════════════════════════════════════════════════════════
//  State
// ═══════════════════════════════════════════════════════════════
let data = null;
let activeLayer = 'ai_exposure';
const mobile = () => window.innerWidth <= 800;

// ═══════════════════════════════════════════════════════════════
//  Formatters
// ═══════════════════════════════════════════════════════════════
function fmtNum(n) {
  if (n >= 1e7) return (n/1e7).toFixed(1).replace(/\.0$/,'') + ' Cr';
  if (n >= 1e5) return (n/1e5).toFixed(1).replace(/\.0$/,'') + 'L';
  if (n >= 1e3) return (n/1e3).toFixed(0) + 'K';
  return n.toLocaleString('en-IN');
}
function fmtWage(w) {
  if (w >= 1e5) return '₹' + (w/1e5).toFixed(1).replace(/\.0$/,'') + 'L/yr';
  return '₹' + Math.round(w/1000) + 'K/yr';
}

// WCAG luminance — pick white or dark text
function useLightText(hex) {
  const c = d3.color(hex);
  if (!c) return false;
  const g = x => { x/=255; return x<=.04045?x/12.92:((x+.055)/1.055)**2.4; };
  return .2126*g(c.r)+.7152*g(c.g)+.0722*g(c.b) < .22;
}

// ═══════════════════════════════════════════════════════════════
//  Colour
// ═══════════════════════════════════════════════════════════════
function colorFor(d) {
  const L = LAYERS[activeLayer];
  if (L.categorical) return L.colors[d.data.growth_outlook] || '#888';
  const v = d.data[activeLayer] ?? 0;
  return L.fn(Math.max(0, Math.min(1, (v - L.domain[0]) / (L.domain[1] - L.domain[0]))));
}

// ═══════════════════════════════════════════════════════════════
//  D3 hierarchy
// ═══════════════════════════════════════════════════════════════
function buildH(occs, groups) {
  const g = {};
  for (const [k,v] of Object.entries(groups)) g[k] = {name:v, code:k, children:[]};
  for (const o of occs) g[o.major_group]?.children.push(o);
  return { name:'root', children: Object.values(g).filter(x=>x.children.length) };
}

// ═══════════════════════════════════════════════════════════════
//  RENDER
// ═══════════════════════════════════════════════════════════════
function render() {
  const el = document.getElementById('treemap');
  const W = el.clientWidth, H = el.clientHeight;
  if (W < 10 || H < 10) return;
  d3.select('#treemap').selectAll('*').remove();

  const svg = d3.select('#treemap').append('svg')
    .attr('width', W).attr('height', H);

  // Power-scale employment so huge groups (agriculture 247M) don't swallow the map
  const root = d3.hierarchy(buildH(data.occupations, data.major_groups))
    .sum(d => d.employment ? Math.pow(d.employment, 0.65) : 0)
    .sort((a,b) => b.value - a.value);

  d3.treemap()
    .size([W, H])
    .paddingOuter(2)
    .paddingTop(13)
    .paddingInner(1)
    .round(true)
    .tile(d3.treemapSquarify.ratio(0.55))(root);

  // ── Group headers ───────────────────────────────
  svg.selectAll('.grp').data(root.children).join('g').attr('class','grp')
    .each(function(d) {
      const G = d3.select(this);
      const gw = d.x1-d.x0, gh = d.y1-d.y0;
      G.append('rect')
        .attr('x',d.x0).attr('y',d.y0)
        .attr('width',gw).attr('height',gh)
        .attr('fill','#F6E5D9').attr('stroke','#E8D5C6')
        .attr('stroke-width',.5).attr('rx',8);
      if (gw > 44) {
        const workers = d.leaves().reduce((s,n)=>s+(n.data.employment||0),0);
        const lbl = d.data.name.toUpperCase();
        const cnt = fmtNum(workers);
        const full = gw > 110 ? `${lbl} · ${cnt}` : lbl;
        const max = Math.floor(gw / 6.8);
        G.append('text').attr('class','grp-lbl')
          .attr('x',d.x0+6).attr('y',d.y0+10)
          .attr('fill','#9A7B60')
          .text(full.length>max ? full.slice(0,max-1)+'…' : full);
      }
    });

  // ── Leaf cells ──────────────────────────────────
  const tt = document.getElementById('tt');

  const cell = svg.selectAll('.cell').data(root.leaves()).join('g')
    .attr('class','cell')
    .attr('transform', d=>`translate(${d.x0},${d.y0})`)
    .style('cursor','pointer');

  cell.append('rect')
    .attr('width',  d => Math.max(0, d.x1-d.x0-1))
    .attr('height', d => Math.max(0, d.y1-d.y0-1))
    .attr('fill', colorFor)
    .attr('rx', 5)
    .attr('stroke','rgba(255,248,244,.6)')
    .attr('stroke-width',.5);

  // Labels
  cell.each(function(d) {
    const cw = d.x1-d.x0, ch = d.y1-d.y0;
    if (cw < 26 || ch < 14) return;
    const fill = colorFor(d);
    const tf = useLightText(fill) ? 'rgba(255,255,255,.93)' : 'rgba(0,0,0,.82)';
    const maxC = Math.floor(cw/5.8);
    const name = d.data.name;
    d3.select(this).append('text').attr('class','cell-name')
      .attr('x',4).attr('y',12).attr('fill',tf)
      .text(name.length>maxC ? name.slice(0,maxC-1)+'…' : name);
    if (ch > 24 && cw > 34) {
      d3.select(this).append('text').attr('class','cell-sub')
        .attr('x',4).attr('y',21).attr('fill',tf).style('opacity',.65)
        .text(fmtNum(d.data.employment));
    }
  });

  // ── Events ──────────────────────────────────────
  cell
    .on('mouseenter', function(_,d) {
      d3.select(this).select('rect')
        .attr('stroke','rgba(0,0,0,.45)').attr('stroke-width',1.5)
        .attr('filter','drop-shadow(0 2px 6px rgba(0,0,0,.25))');
    })
    .on('mousemove', function(event, d) {
      const gc = LAYERS.growth_outlook.colors[d.data.growth_outlook];
      tt.innerHTML = `
        <div class="tt-name">${d.data.name}</div>
        <div class="tt-val">${LAYERS[activeLayer].tip(d.data)}</div>
        <div class="tt-row">${fmtNum(d.data.employment)} workers · ${fmtWage(d.data.median_wage)}</div>
        <div class="tt-row"><span class="tt-dot" style="background:${gc}"></span>${d.data.growth_outlook} · ${d.data.informal_pct}% informal</div>
      `;
      tt.classList.add('vis');
      const tx = event.clientX+16, ty = event.clientY-8;
      tt.style.left = Math.min(tx, window.innerWidth-245)+'px';
      tt.style.top  = Math.max(4, Math.min(ty, window.innerHeight-110))+'px';
    })
    .on('mouseleave', function() {
      d3.select(this).select('rect')
        .attr('stroke','rgba(255,255,255,.55)').attr('stroke-width',.5)
        .attr('filter',null);
      tt.classList.remove('vis');
    })
    .on('click', (_,d) => {
      if (mobile()) showMob(d.data);
      else          showCard(d.data);
    });
}

// ═══════════════════════════════════════════════════════════════
//  Update colours only
// ═══════════════════════════════════════════════════════════════
function updateColors() {
  d3.select('#treemap').selectAll('.cell').each(function(d) {
    const fill = colorFor(d);
    const tf = useLightText(fill) ? 'rgba(255,255,255,.93)' : 'rgba(0,0,0,.82)';
    d3.select(this).select('rect').transition().duration(220).attr('fill', fill);
    d3.select(this).selectAll('text').attr('fill', tf);
  });
  renderLegend();
}

// ═══════════════════════════════════════════════════════════════
//  Legend
// ═══════════════════════════════════════════════════════════════
function renderLegend() {
  const L = LAYERS[activeLayer];
  const inner = document.getElementById('legend-inner');
  const sw    = document.getElementById('legend-swatches');
  sw.innerHTML = '';

  if (L.categorical) {
    inner.style.display = 'none';
    for (const k of GROWTH_ORDER) {
      const item = document.createElement('div');
      item.className = 'ls-item';
      item.innerHTML = `<span class="ls-dot" style="background:${L.colors[k]}"></span><span>${k}</span>`;
      sw.appendChild(item);
    }
  } else {
    inner.style.display = 'flex';
    const N=24, stops = Array.from({length:N},(_,i)=>L.fn(i/(N-1))).join(',');
    document.getElementById('legend-grad').style.background = `linear-gradient(to right,${stops})`;
    document.getElementById('legend-low').textContent = L.lo;
    document.getElementById('legend-high').textContent = L.hi;
  }
}

// ═══════════════════════════════════════════════════════════════
//  Radar chart — light theme
// ═══════════════════════════════════════════════════════════════
function drawRadar(svgId, d) {
  const S=128, cx=S/2, cy=S/2, R=40;
  const N = SCORES.length;
  const ang = i => (i/N)*2*Math.PI - Math.PI/2;
  const px  = (i,v) => cx + R*(v/10)*Math.cos(ang(i));
  const py  = (i,v) => cy + R*(v/10)*Math.sin(ang(i));

  const svg = d3.select('#'+svgId).attr('width',S).attr('height',S);
  svg.selectAll('*').remove();

  [2,4,6,8,10].forEach(v => {
    const pts = SCORES.map((_,i)=>`${px(i,v)},${py(i,v)}`).join(' ');
    svg.append('polygon').attr('points',pts)
      .attr('fill', v===10?'rgba(246,229,217,.7)':'none')
      .attr('stroke','#E0CDBD').attr('stroke-width', v===10?1:.5);
  });
  SCORES.forEach((_,i)=>svg.append('line')
    .attr('x1',cx).attr('y1',cy).attr('x2',px(i,10)).attr('y2',py(i,10))
    .attr('stroke','#DCC8B8').attr('stroke-width',.8));

  const pts = SCORES.map((s,i)=>`${px(i,d[s.key]||0)},${py(i,d[s.key]||0)}`).join(' ');
  svg.append('polygon').attr('points',pts)
    .attr('fill','rgba(212,88,10,.12)')
    .attr('stroke','#D4580A').attr('stroke-width',1.5).attr('stroke-linejoin','round');

  SCORES.forEach((s,i)=>svg.append('circle')
    .attr('cx',px(i,d[s.key]||0)).attr('cy',py(i,d[s.key]||0))
    .attr('r',3).attr('fill',s.color)
    .attr('stroke','#FFFFFF').attr('stroke-width',1.5));

  const LR=R+16;
  SCORES.forEach((s,i)=>svg.append('text')
    .attr('x',cx+LR*Math.cos(ang(i))).attr('y',cy+LR*Math.sin(ang(i)))
    .attr('text-anchor','middle').attr('dominant-baseline','middle')
    .attr('fill','#8A7A65')
    .style('font-family','Poppins,sans-serif')
    .style('font-size','7px').style('font-weight','600')
    .text(s.label));
}

// ═══════════════════════════════════════════════════════════════
//  Info card HTML builder
// ═══════════════════════════════════════════════════════════════
function cardHTML(d) {
  const gc = LAYERS.growth_outlook.colors[d.growth_outlook]||'#888';
  return {
    gc,
    stats: `
      <div class="fc-cell"><div class="fc-val">${fmtNum(d.employment)}</div><div class="fc-lbl">Workers</div></div>
      <div class="fc-cell"><div class="fc-val">${fmtWage(d.median_wage)}</div><div class="fc-lbl">Median wage</div></div>
      <div class="fc-cell"><div class="fc-val">${d.informal_pct}%</div><div class="fc-lbl">Informal</div></div>
      <div class="fc-cell"><div class="fc-val">${d.rural_pct}%</div><div class="fc-lbl">Rural</div></div>
    `,
    scores: SCORES.map(s=>`
      <div class="sc-row">
        <div class="sc-head"><span>${s.label}</span><span>${d[s.key]??'--'}/10</span></div>
        <div class="sc-track"><div class="sc-fill" style="width:${(d[s.key]||0)*10}%;background:${s.color}"></div></div>
      </div>`).join(''),
  };
}

// ═══════════════════════════════════════════════════════════════
//  Desktop floating card
// ═══════════════════════════════════════════════════════════════
function showCard(d) {
  const card = document.getElementById('float-card');
  card.classList.remove('hidden');
  const {gc, stats, scores} = cardHTML(d);

  document.getElementById('fc-vintage').textContent = d.data_vintage || 'PLFS 2023-24';
  document.getElementById('fc-name').textContent    = d.name;
  document.getElementById('fc-meta').textContent    = `NCO ${d.code} · ${d.major_group_name}`;
  document.getElementById('fc-growth').innerHTML    = `<span class="g-pill" style="background:${gc}18;color:${gc};border:1px solid ${gc}55">${d.growth_outlook}</span>`;
  document.getElementById('fc-stats').innerHTML     = stats;
  document.getElementById('fc-scores').innerHTML    = scores;
  document.getElementById('fc-india').textContent   = d.india_note || '';
  document.getElementById('fc-rationale').textContent = `"${d.ai_rationale}"`;
  drawRadar('fc-radar-svg', d);
}

// ═══════════════════════════════════════════════════════════════
//  Mobile bottom sheet
// ═══════════════════════════════════════════════════════════════
function showMob(d) {
  const {gc, stats, scores} = cardHTML(d);
  document.getElementById('mob-body').innerHTML = `
    <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.9px;color:var(--text4);margin-bottom:4px">${d.data_vintage||'PLFS 2023-24'}</div>
    <div style="font-size:16px;font-weight:800;color:var(--text);margin-bottom:2px;padding-right:28px;line-height:1.3">${d.name}</div>
    <div style="font-size:10px;font-weight:300;color:var(--text3);margin-bottom:8px">NCO ${d.code} · ${d.major_group_name}</div>
    <span class="g-pill" style="background:${gc}18;color:${gc};border:1px solid ${gc}55;margin-bottom:10px;display:inline-block">${d.growth_outlook}</span>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:10px">${stats}</div>
    <div style="display:flex;justify-content:center;padding:8px 0 10px;border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin-bottom:10px">
      <svg id="mob-radar-svg"></svg>
    </div>
    <div>${scores}</div>
    <div id="fc-india" style="font-size:10.5px;font-weight:300;color:var(--text2);line-height:1.65;background:var(--green-bg);border-left:2.5px solid var(--green);padding:7px 9px;border-radius:0 4px 4px 0;margin:7px 0">${d.india_note||''}</div>
    <div style="font-size:9.5px;font-weight:300;font-style:italic;color:var(--text3);line-height:1.6;border-top:1px solid var(--border);padding-top:7px">"${d.ai_rationale}"</div>
  `;
  document.getElementById('mob-sheet').classList.remove('mob-hidden');
  document.getElementById('mob-veil').classList.remove('mob-hidden');
  drawRadar('mob-radar-svg', d);
}

function closeMob() {
  document.getElementById('mob-sheet').classList.add('mob-hidden');
  document.getElementById('mob-veil').classList.add('mob-hidden');
}

// ═══════════════════════════════════════════════════════════════
//  Stats
// ═══════════════════════════════════════════════════════════════
function populateStats() {
  const total = data.occupations.reduce((s,o)=>s+o.employment,0);
  document.getElementById('hdr-workers').textContent = fmtNum(total);
  document.getElementById('hdr-occ').textContent     = data.occupations.length;
  document.getElementById('leg-workers').textContent = fmtNum(total);
}

// ═══════════════════════════════════════════════════════════════
//  Events
// ═══════════════════════════════════════════════════════════════
document.querySelectorAll('.lb').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.lb').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    activeLayer = btn.dataset.layer;
    updateColors();
  });
});

document.getElementById('fc-close').addEventListener('click', () =>
  document.getElementById('float-card').classList.add('hidden'));
document.getElementById('mob-close').addEventListener('click', closeMob);
document.getElementById('mob-veil').addEventListener('click', closeMob);

new ResizeObserver(() => { if (data) render(); })
  .observe(document.getElementById('treemap'));

// ═══════════════════════════════════════════════════════════════
//  Init
// ═══════════════════════════════════════════════════════════════
function setup(json) {
  data = json;
  populateStats();
  render();
  renderLegend();
}

function showErr(msg) {
  document.getElementById('treemap').innerHTML = `
    <div style="padding:40px;font-family:Poppins,sans-serif;color:#C62828;font-size:13px">
      <strong>Could not load occupations data</strong><br><br>${msg}<br><br>
      <span style="color:var(--text3);font-size:11px">
        Run: <code style="background:#F5F5F5;padding:2px 6px;border-radius:3px;border:1px solid #E0D9CE">python -m http.server 8000</code>
        then open <a href="http://localhost:8000" style="color:#D4580A">localhost:8000</a>
      </span>
    </div>`;
}

// window.JOBS_DATA set by data/occupations.js (works on file://)
// fallback to fetch for GitHub Pages / HTTP server
if (window.JOBS_DATA) {
  setup(window.JOBS_DATA);
} else {
  fetch('data/occupations.json')
    .then(r => { if(!r.ok) throw new Error(r.statusText); return r.json(); })
    .then(setup)
    .catch(e => showErr(e.message));
}
