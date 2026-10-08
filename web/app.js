(function () {
'use strict';
const CJK = /[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/;
const CATALOG = window.IMDG_CATALOG, DGL = window.DGL, CLAUSES = window.CLAUSES,
      IDX = window.IDX, CHG = window.CHANGELOG, SI = window.SINDEX;

/* ---------------- 文本归一化 / 分词 ---------------- */
function normalize(s) {
  s = (s || '').replace(/\u00a0/g, ' ');
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (ch === ' ') {
      const p = s[i - 1] || '', n = s[i + 1] || '';
      if (CJK.test(p) || CJK.test(n)) continue;
      out += ' ';
    } else out += ch;
  }
  return out.replace(/\s+/g, ' ').trim();
}
function tokenize(text) {
  const toks = [];
  let i = 0;
  while (i < text.length) {
    if (CJK.test(text[i])) {
      let j = i; while (j < text.length && CJK.test(text[j])) j++;
      const run = text.slice(i, j);
      for (let k = 0; k + 1 < run.length; k++) toks.push(run.substr(k, 2));
      i = j;
    } else if (/[A-Za-z0-9]/.test(text[i])) {
      let j = i; while (j < text.length && /[A-Za-z0-9]/.test(text[j])) j++;
      toks.push(text.slice(i, j).toLowerCase());
      i = j;
    } else i++;
  }
  return toks;
}
function disp(s) { return normalize(s); }
function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
function hl(text, q) {
  const t = esc(text);
  if (!q || q.length < 1) return t;
  const eq = esc(q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  try { return t.replace(new RegExp(eq, 'gi'), m => '<mark>' + m + '</mark>'); } catch (e) { return t; }
}

/* ---------------- 文档集合 ---------------- */
const DOCS = [];
const DGL_DFIELDS = [['cls', '类别'], ['sub', '副危险'], ['pg', '包装类'], ['sp', '特殊规定'],
  ['lq', '限量'], ['eq', '可免除量'], ['pkg', '包装导则'], ['pkgprov', '包装特殊规定'],
  ['ibc', 'IBC导则'], ['ibcprov', 'IBC特殊规定'], ['tank', '罐柜导则'],
  ['tankprov', '罐柜特殊规定'], ['ems', 'EmS'], ['stow', '积载与操作'], ['seg', '隔离'],
  ['prop', '特性与注意事项']];

DGL.forEach((r, i) => {
  const text = normalize(['UN ' + r.un, r.psn, r.cls, r.sub, r.sp, r.pkg, r.pkgprov, r.ibc,
    r.tank, r.ems, r.stow, r.seg, r.prop].join(' '));
  DOCS.push({ k: 'd', i, title: 'UN ' + r.un + ' ' + normalize(r.psn), sub: '第' + r.cls + '类 / 包装类' + (r.pg || '-') + ' / ' + r.ems,
    page: r.page, text });
});
CLAUSES.forEach((c, i) => {
  const title = c.id + (c.text ? ' ' + c.text.split('\n')[0].slice(0, 46) : '');
  DOCS.push({ k: 'c', i, title: title.trim(),
    sub: (c.chapter ? c.chapter + ' ' + (c.chapterTitle || '') : (c.part + ' ' + (c.partTitle || ''))).trim(),
    page: c.page, text: normalize([c.id, c.chapterTitle, c.text].join(' ')) });
});
IDX.forEach((e, i) => {
  DOCS.push({ k: 'i', i, title: e.name, sub: 'UN ' + e.un + ' / 第' + e.cls + (e.mp === 'P' ? '类 · 海洋污染物' : '类'),
    page: e.page, text: normalize([e.name, e.un, e.cls].join(' ')) });
});

/* ---------------- 倒排索引 ---------------- */
const TERM_IDX = new Map();
SI.terms.forEach((t, i) => TERM_IDX.set(t, i));
const POST_CACHE = new Map();
function b64bytes(b64) {
  const bin = atob(b64), u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
}
function postings(term) {
  if (POST_CACHE.has(term)) return POST_CACHE.get(term);
  const ti = TERM_IDX.get(term);
  let list = null;
  if (ti !== undefined) {
    const u = b64bytes(SI.postings[ti]);
    list = [];
    let p = 0, doc = 0;
    while (p < u.length) {
      let sh = 0, d = 0, b;
      do { b = u[p++]; d |= (b & 0x7f) << sh; sh += 7; } while (b & 0x80);
      doc += d;
      let tf = 0; sh = 0;
      do { b = u[p++]; tf |= (b & 0x7f) << sh; sh += 7; } while (b & 0x80);
      list.push(doc, tf);
    }
  }
  POST_CACHE.set(term, list);
  return list;
}
const AVG = SI.avgLen, NDOC = SI.docCount, LEN = SI.lengths, K1 = 1.2, B = 0.75;
function bm25(tokens) {
  const sc = new Map(), seen = new Set();
  const uniq = [];
  tokens.forEach(t => { if (!seen.has(t)) { seen.add(t); uniq.push(t); } });
  uniq.forEach(term => {
    const list = postings(term);
    if (!list) return;
    const df = list.length / 2;
    const idf = Math.log(1 + (NDOC - df + 0.5) / (df + 0.5));
    for (let i = 0; i < list.length; i += 2) {
      const d = list[i], tf = list[i + 1];
      const s = idf * (tf * (K1 + 1)) / (tf + K1 * (1 - B + B * LEN[d] / AVG));
      sc.set(d, (sc.get(d) || 0) + s);
    }
  });
  return sc;
}

/* ---------------- 查询 ---------------- */
const HINTS = {
  un: '按联合国编号（第1栏）精确检索',
  clause: '按条款号检索规则原文',
  code: '按代码检索定义/规定',
  kw: '全文检索（中文二元组 + 英文/数字词）'
};
function parseQuery(raw) {
  const q = raw.trim();
  if (!q) return { mode: 'empty' };
  let m;
  if ((m = q.match(/^(?:un[\s\-]?)?(\d{4})$/i))) return { mode: 'un', v: m[1] };
  if ((m = q.match(/^sp\s?(\d{1,3})$/i))) return { mode: 'clause', v: 'SP' + m[1], label: 'SP' + m[1] };
  if ((m = q.match(/^(p|lp|ibc|bk)\s?(\d{1,3})$/i))) {
    const pre = m[1].toUpperCase();
    const num = pre === 'P' || pre === 'LP' ? m[2].padStart(3, '0') : m[2].padStart(2, '0');
    return { mode: 'clause', v: pre + num, label: pre + num };
  }
  if ((m = q.match(/^t\s?(\d{1,2})$/i))) return { mode: 'clause', v: 'T' + m[1], label: 'T' + m[1] };
  if (/^[fs]\-[a-z]$/i.test(q)) return { mode: 'kw', v: q.toUpperCase(), note: 'EmS 代码见《EmS 指南》，本页面可检索引用该代码的条目' };
  if ((m = q.match(/^(\d+(?:\.\d+){1,4})$/))) return { mode: 'clause', v: m[1], label: m[1] };
  return { mode: 'kw', v: q };
}
const NDGL = DGL.length, NCLAUSE = CLAUSES.length;
const DOC_DGL = i => DOCS[i];
const DOC_CLAUSE = i => DOCS[NDGL + i];
const DOC_IDX = i => DOCS[NDGL + NCLAUSE + i];
function search(raw) {
  const q = parseQuery(raw);
  q.raw = raw.trim();
  if (q.mode === 'empty') return { q, hits: [] };
  const out = [];
  const upper = q.v.toUpperCase();
  if (q.mode === 'un') {
    for (let i = 0; i < NDGL; i++) if (DGL[i].un === q.v) out.push({ d: DOC_DGL(i), score: 1000 });
    for (let i = 0; i < IDX.length; i++) if (IDX[i].un === q.v) out.push({ d: DOC_IDX(i), score: 600 });
    for (let i = 0; i < NCLAUSE; i++) if (CLAUSES[i].text && CLAUSES[i].text.indexOf(q.v) >= 0)
      out.push({ d: DOC_CLAUSE(i), score: 100 });
  } else if (q.mode === 'clause') {
    for (let i = 0; i < NCLAUSE; i++) {
      const id = CLAUSES[i].id.toUpperCase();
      if (id === upper) out.push({ d: DOC_CLAUSE(i), score: 1000 });
      else if (id.startsWith(upper + '.')) out.push({ d: DOC_CLAUSE(i), score: 500 - id.length });
    }
    if (!out.length) q.mode = 'kw';
  }
  if (q.mode === 'kw') {
    const toks = tokenize(normalize(q.v));
    const phrase = normalize(q.v).toLowerCase();
    if (toks.length) {
      const sc = bm25(toks);
      sc.forEach((s, d) => {
        const bonus = DOCS[d].text.toLowerCase().indexOf(phrase) >= 0 ? 8 : 0;
        out.push({ d: DOCS[d], score: s + bonus });
      });
    }
    if (!toks.length || out.length < 3) {
      DOCS.forEach(d => { if (d.text.indexOf(phrase) >= 0) out.push({ d, score: 40 }); });
    }
  }
  out.sort((a, b) => b.score - a.score || a.d.k.localeCompare(b.d.k));
  const seen = new Set(), ded = [];
  for (const h of out) {
    const key = h.d.k + ':' + h.d.i;
    if (seen.has(key)) continue;
    seen.add(key);
    ded.push(h);
  }
  return { q, hits: ded.slice(0, 150) };
}
/* ---------------- 渲染 ---------------- */
function snippet(text, q, width) {
  width = width || 130;
  const i = text.toLowerCase().indexOf(normalize(q).toLowerCase());
  if (i < 0) return text.slice(0, width) + (text.length > width ? ' …' : '');
  const a = Math.max(0, i - Math.floor(width / 3));
  return (a > 0 ? '… ' : '') + text.slice(a, a + width) + (a + width < text.length ? ' …' : '');
}
const KINDNAME = { d: '货物条目', c: '规则条款', i: '索引' };
function resRow(h, q, sel) {
  const d = h.d;
  const show = d.k === 'd' ? d.text : snippet(d.text, q.v);
  return '<div class="res' + (sel ? ' sel' : '') + '" data-key="' + d.k + ':' + d.i + '">' +
    '<div class="t"><span class="badge ' + d.k + '">' + KINDNAME[d.k] + '</span><span>' + hl(d.title, q.v) + '</span></div>' +
    '<div class="s">' + hl(show, q.v) + '</div>' +
    '<div class="p"><span>' + esc(d.sub) + '</span><span>原书 p.' + d.page + '</span>' +
    (d.k === 'd' && CHG.byUn[DGL[d.i].un] ? '<span class="tag42">42-24 已修订</span>' : '') + '</div></div>';
}
function chip(code, cls) {
  return '<span class="chip ' + (cls || '') + '" data-code="' + esc(code) + '">' + esc(code) + '</span>';
}
function codes(str, cls) {
  if (!str || str === '-' || str === '–') return '<span class="muted">–</span>';
  return str.split(/\s+/).filter(Boolean).map(c => chip(c, cls)).join('');
}
function dglDetail(r) {
  const rows = DGL_DFIELDS.map(([k, label]) => {
    let v = r[k] || '';
    if (k === 'sp' || k === 'pkg' || k === 'tank' || k === 'ibc') return '<div class="k">' + label + '</div><div class="v">' + codes(v, k === 'sp' ? 'sp' : 'pk') + '</div>';
    if (k === 'pkgprov' || k === 'tankprov' || k === 'ibcprov') return '<div class="k">' + label + '</div><div class="v">' + codes(v, 'pk') + '</div>';
    if (k === 'stow' || k === 'seg') return '<div class="k">' + label + '</div><div class="v">' + codes(v) + '</div>';
    return '<div class="k">' + label + '</div><div class="v">' + esc(disp(v) || '–') + '</div>';
  }).join('');
  const chg = CHG.byUn[r.un];
  return '<div class="card-h"><span class="ttl">UN ' + r.un + '</span>' +
    (chg ? '<span class="tag42">42-24 已修订</span>' : '') + '</div>' +
    '<div style="font-size:15px;font-weight:600;margin-bottom:8px">' + esc(disp(r.psn)) + '</div>' +
    '<div class="fields">' + rows + '</div>' +
    (chg ? '<div class="chg"><b>42-24 修正案改动</b><br>' + esc(chg.join('\n')) + '</div>' : '') +
    '<div class="muted" style="margin-top:8px;font-size:12px">原书页码 p.' + r.page + '（危险货物一览表 第3.2章）</div>';
}
function clauseDetail(c) {
  const chg = CHG.byClause[c.id] || CHG.bySp[c.id];
  return '<div class="card-h"><span class="ttl">' + esc(c.id) + '</span>' +
    (chg ? '<span class="tag42">42-24 已修订</span>' : '') + '</div>' +
    '<div class="muted" style="font-size:12.5px">' + esc([c.part, c.partTitle, c.chapter, c.chapterTitle].filter(Boolean).join(' · ')) + '</div>' +
    '<div class="clause">' + esc(c.text || '（本节为标题，正文见下级条款）') + '</div>' +
    (chg ? '<div class="chg"><b>42-24 修正案改动</b><br>' + esc(chg.join('\n')) + '</div>' : '') +
    '<div class="muted" style="margin-top:8px;font-size:12px">原书页码 p.' + c.page + '</div>';
}
function idxDetail(e) {
  return '<div class="card-h"><span class="ttl">' + esc(e.name) + '</span></div>' +
    '<div class="fields"><div class="k">联合国编号</div><div class="v">' + chip('UN ' + e.un) + '</div>' +
    '<div class="k">类别</div><div class="v">第' + esc(e.cls) + '类</div>' +
    '<div class="k">海洋污染物</div><div class="v">' + (e.mp === 'P' ? '是' : '否') + '</div></div>' +
    '<div class="muted" style="margin-top:8px;font-size:12px">原书页码 p.' + e.page + '（书末索引）</div>';
}
function showDetail(dk, di, target) {
  const el = document.getElementById(target || 'detail');
  if (dk === 'd') el.innerHTML = dglDetail(DGL[di]);
  else if (dk === 'c') el.innerHTML = clauseDetail(CLAUSES[di]);
  else el.innerHTML = idxDetail(IDX[di]);
  el.querySelectorAll('.chip[data-code]').forEach(ch => ch.onclick = () => submit(ch.dataset.code));
}
let lastHits = [];
function render(hits, q) {
  lastHits = hits;
  const box = document.getElementById('results');
  const meta = document.getElementById('resultMeta');
  if (!hits.length) { box.innerHTML = '<div class="empty">无匹配结果</div>'; meta.textContent = '无结果'; return; }
  const counts = hits.reduce((a, h) => (a[h.d.k] = (a[h.d.k] || 0) + 1, a), {});
  meta.textContent = '“' + q.raw + '” · ' + (HINTS[q.mode] || HINTS.kw) + ' · 共 ' + hits.length + ' 条' +
    (q.note ? ' · ' + q.note : '');
  box.innerHTML = hits.map((h, i) => resRow(h, q, i === 0)).join('');
  box.querySelectorAll('.res').forEach((el, i) => el.onclick = () => {
    box.querySelectorAll('.res').forEach(x => x.classList.remove('sel'));
    el.classList.add('sel');
    const [k, id] = el.dataset.key.split(':');
    showDetail(k, +id);
  });
  const first = box.querySelector('.res');
  if (first) { const [k, id] = first.dataset.key.split(':'); showDetail(k, +id); }
}
function submit(v) {
  document.getElementById('q').value = v;
  doSearch();
}
function doSearch() {
  const raw = document.getElementById('q').value;
  const res = search(raw);
  if (res.q.mode === 'empty') { document.getElementById('resultMeta').textContent = '输入条件开始检索'; return; }
  const on = new Set([...document.querySelectorAll('#typeFilter input:checked')].map(x => x.dataset.k));
  render(res.hits.filter(h => on.has(h.d.k)), res.q);
}

/* ---------------- 视图切换 ---------------- */
document.querySelectorAll('nav.tabs button').forEach(b => b.onclick = () => {
  document.querySelectorAll('nav.tabs button').forEach(x => x.classList.toggle('active', x === b));
  document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', v.id === 'view-' + b.dataset.view));
});

/* ---------------- 变更清单 ---------------- */
let chgFilterPart = '';
function chgRender() {
  const kw = document.getElementById('chgFilter').value.trim();
  const items = CHG.items.filter(it => ['clause', 'sp', 'un'].indexOf(it.kind) >= 0
    && (!chgFilterPart || it.part === chgFilterPart)
    && (!kw || (it.ref + it.text + it.chapter).indexOf(kw) >= 0));
  const list = document.getElementById('chgList');
  list.innerHTML = items.length ? items.map(it => {
    const loc = [it.part, it.chapter, it.section].filter(Boolean).join(' · ');
    const kind = it.kind === 'un' ? '危险货物一览表（第3.2章）条目' : (it.kind === 'sp' ? '特殊规定' : '条款');
    return '<div class="cg"><div class="r"><span>' + esc(it.ref) + '</span><span class="loc">' + kind + ' · ' + esc(loc) + ' · 清单第' + it.page + '页</span></div>' +
      '<div class="b">' + esc(it.text) + '</div></div>';
  }).join('') : '<div class="empty">无匹配</div>';
  const cc = document.getElementById('chgCount'); if (cc) cc.textContent = items.length + ' 条';
}
function initChanges() {
  const s = CHG.stats;
  document.getElementById('chgStats').innerHTML =
    card(s.unChanged, '危险货物一览表改动的UN条目') + card(s.clausesChanged, '改动的条款') +
    card(s.spChanged, '改动的特殊规定') + card(s.items, '清单条目总数') +
    card('7/7', '涉及的部分（全部第1—7部分）');
  const parts = [...new Set(CHG.items.map(i => i.part).filter(Boolean))];
  document.getElementById('chgParts').innerHTML =
    '<button class="on" data-p="">全部</button>' + parts.map(p => '<button data-p="' + esc(p) + '">' + esc(p) + '</button>').join('');
  document.getElementById('chgParts').querySelectorAll('button').forEach(b => b.onclick = () => {
    chgFilterPart = b.dataset.p;
    document.getElementById('chgParts').querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
    chgRender();
  });
  document.getElementById('chgFilter').oninput = chgRender;
  chgRender();
}
function card(n, l) { return '<div class="c"><div class="n">' + esc(n) + '</div><div class="l">' + esc(l) + '</div></div>'; }

/* ---------------- 分类浏览 ---------------- */
function initBrowse() {
  const tree = document.getElementById('tree');
  let html = '';
  const groups = {};
  CLAUSES.forEach((c, i) => {
    const key = c.chapter || c.part || '其他';
    (groups[key] = groups[key] || { title: c.chapterTitle || c.partTitle || '', items: [] }).items.push(i);
  });
  Object.keys(groups).sort().forEach(k => {
    html += '<div class="pc">' + esc(k) + ' ' + esc(groups[k].title.slice(0, 18)) + '</div>';
    groups[k].items.slice(0, 6).forEach(i => {
      html += '<a data-i="' + i + '">' + esc(CLAUSES[i].id) + '</a>';
    });
    if (groups[k].items.length > 6) html += '<a data-chap="' + esc(k) + '" class="muted">… 全部 ' + groups[k].items.length + ' 条</a>';
  });
  tree.innerHTML = html;
  tree.querySelectorAll('a').forEach(a => a.onclick = () => {
    if (a.dataset.i !== undefined) {
      const c = CLAUSES[+a.dataset.i];
      document.getElementById('browseList').innerHTML = '<div class="res sel"><div class="t">' + esc(c.id) + '</div><div class="s">' + esc((c.chapterTitle || '')) + '</div></div>';
      showDetail('c', +a.dataset.i, 'detail2');
    } else {
      const items = CLAUSES.map((c, i) => [c, i]).filter(([c]) => (c.chapter || c.part || '其他') === a.dataset.chap);
      document.getElementById('browseList').innerHTML = items.map(([c, i]) =>
        '<div class="res" data-i="' + i + '"><div class="t"><span class="badge c">条款</span>' + esc(c.id) + '</div><div class="s">' + esc((c.text || '').slice(0, 90)) + '</div></div>').join('');
      document.getElementById('browseList').querySelectorAll('.res').forEach(el => el.onclick = () => showDetail('c', +el.dataset.i, 'detail2'));
    }
  });
}

/* ---------------- 说明 ---------------- */
function initAbout() {
  const s = CATALOG.stats;
  document.getElementById('about').innerHTML =
    '<h2>这个 Demo 是什么</h2>' +
    '<p>把《国际海运危险货物规则》中文版 PDF 自动拆解成可检索的结构化数据，做成一个离线网页。当前数据：危险货物一览表 <b>' + s.dglRows + '</b> 行（<b>' + s.dglUn + '</b> 个 UN 编号）、规则条款 <b>' + s.clauses + '</b> 段、特殊规定 <b>' + s.sp + '</b> 条、书末索引 <b>' + s.indexEntries + '</b> 条，全部来自 1372 页原文。</p>' +
    '<h2>原理（数据管线）</h2>' +
    '<table><tr><th>步骤</th><th>做法</th></tr>' +
    '<tr><td>1 取文字</td><td>PyMuPDF 逐页取词（含坐标），去掉页眉页脚（MSC 编号、DANKA 文件名、页码）</td></tr>' +
    '<tr><td>2 认表格</td><td>一览表用“表格边框横线”定位每一行、用 22 条竖线定位 21 列；行锚点＝第1栏/第18栏的 4 位 UN 号</td></tr>' +
    '<tr><td>3 拼单元格</td><td>按坐标把词归到行列，跨行断字按“上一行是否顶到列右边”判断是否补空格（IBC02、500mL）</td></tr>' +
    '<tr><td>4 切条款</td><td>按条款号（4.1.1.3）、代码（P001/IBC02/T4/SP310）切分正文，记下部分/章上下文与原书页码</td></tr>' +
    '<tr><td>5 建索引</td><td>中文按“二元组”切词、英文/数字按单词，生成倒排索引（含词频），前端用 BM25 打分</td></tr>' +
    '<tr><td>6 提精度</td><td>命中后再做一次“原句包含”校验并加权，避免二元组误召回</td></tr></table>' +
    '<h2>怎么用</h2>' +
    '<ul class="plain"><li><b>UN 号</b>：<code>1203</code>、<code>UN 3082</code> → 直达一览表条目（同一 UN 多个包装类会分行显示）</li>' +
    '<li><b>条款号</b>：<code>7.1.5</code>、<code>4.1.4.1</code> → 规则原文</li>' +
    '<li><b>代码</b>：<code>SP310</code>、<code>P001</code>、<code>IBC02</code>、<code>T4</code>、<code>BK1</code> → 定义与规定</li>' +
    '<li><b>关键词</b>：<code>锂离子电池</code>、<code>积载类E</code>、<code>SGG2</code>、<code>海洋污染物</code> → 全文检索（中英数字混排都可以）</li>' +
    '<li>条目卡片里的每个代码都是可点的，点了就跳到它的定义</li></ul>' +
    '<h2>已知边界（Demo 阶段）</h2>' +
    '<ul class="plain"><li>原文是中文译本，个别译名/数值需与英文原版核对（例如 UN 3560 的中文名，两份中文文件就不一致）</li>' +
    '<li>表格按几何规则解析，极少数跨页或空单元格仍需人工复核</li>' +
    '<li>EmS 代码、MFAG 等《补充本》内容不在这本 PDF 里，只能检索到引用它的条目</li>' +
    '<li>没有做中文分词词典，用的是二元组；正式版建议加专业词表与同义词</li></ul>';
}

/* ---------------- 启动 ---------------- */
function initFacets() {
  const counts = { d: DGL.length, c: CLAUSES.length, i: IDX.length };
  document.getElementById('typeFilter').innerHTML = ['d', 'c', 'i'].map(k =>
    '<label><input type="checkbox" checked data-k="' + k + '">' + KINDNAME[k] + '<span class="cnt">' + counts[k] + '</span></label>').join('');
  document.getElementById('typeFilter').onchange = () => {
    const on = new Set([...document.querySelectorAll('#typeFilter input:checked')].map(x => x.dataset.k));
    const raw = document.getElementById('q').value;
    const { q, hits } = search(raw);
    render(hits.filter(h => on.has(h.d.k)), q);
  };
  const quick = [['UN 1203 车用汽油', '1203'], ['锂离子电池', '锂离子电池'], ['积载类E', '积载类E'],
    ['隔离表 SGG2', 'SGG2'], ['特殊规定 SP310', 'SP310'], ['包装导则 P001', 'P001'],
    ['海洋污染物', '海洋污染物'], ['第7.1章 积载', '7.1'], ['术语汇编', '术语汇编']];
  document.getElementById('quick').innerHTML = quick.map(([t, v]) => '<a data-q="' + esc(v) + '">' + esc(t) + '</a>').join('');
  document.getElementById('quick').querySelectorAll('a').forEach(a => a.onclick = () => submit(a.dataset.q));
  const s = CATALOG.stats;
  document.getElementById('scale').innerHTML =
    '<div><span>一览表行数</span><b>' + s.dglRows + '</b></div>' +
    '<div><span>UN 编号</span><b>' + s.dglUn + '</b></div>' +
    '<div><span>规则条款</span><b>' + s.clauses + '</b></div>' +
    '<div><span>特殊规定</span><b>' + s.sp + '</b></div>' +
    '<div><span>包装导则等代码</span><b>' + s.codes + '</b></div>' +
    '<div><span>索引条目</span><b>' + s.indexEntries + '</b></div>' +
    '<div><span>原文页数</span><b>' + s.pages + '</b></div>';
}
function boot() {
  document.getElementById('stats').textContent = '一览表 ' + CATALOG.stats.dglRows + ' 行 / 条款 ' + CATALOG.stats.clauses + ' 段 / 索引 ' + CATALOG.stats.indexEntries + ' 条';
  initFacets(); initChanges(); initBrowse(); initAbout();
  document.getElementById('go').onclick = doSearch;
  document.getElementById('q').addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
  let timer = null;
  document.getElementById('q').addEventListener('input', e => {
    clearTimeout(timer);
    timer = setTimeout(() => { if (e.target.value.trim().length >= 2) doSearch(); }, 220);
  });
  doSearch();
}
window.__IMDG = { search, parseQuery, DOCS, DGL, CLAUSES, IDX, CHG, tokenize, normalize, dglDetail, clauseDetail, idxDetail, resRow, CATALOG };
document.addEventListener('DOMContentLoaded', boot);
})();