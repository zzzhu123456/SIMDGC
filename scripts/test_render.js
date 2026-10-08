global.window = {};
global.atob = s => Buffer.from(s, 'base64').toString('binary');
const stubEl = () => ({ innerHTML:'', textContent:'', value:'', dataset:{}, style:{},
  classList:{add(){},remove(){},toggle(){}}, querySelectorAll:()=>[], querySelector:()=>null,
  addEventListener(){}, onclick:null });
global.document = { getElementById: () => stubEl(), querySelectorAll: () => [], addEventListener: () => {} };
const fs = require('fs');
for (const n of ['catalog','dgl','clauses','idx','changelog','sindex']) eval(fs.readFileSync('web/data/'+n+'.js','utf8'));
eval(fs.readFileSync('web/app.js','utf8'));
const S = window.__IMDG;
const strip = h => h.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
console.log('--- DGL card: UN 1203 / 3082 / 3480 / 3560 ---');
for (const un of ['1203','3082','3480','3560']) {
  const r = S.DGL.find(x => x.un === un);
  const h = S.dglDetail(r);
  console.log('UN ' + un + ' -> chips=' + (h.match(/class="chip/g)||[]).length + ' | ' + strip(h).slice(0, 200));
}
console.log('\n--- clause card SP310 ---');
const c = S.CLAUSES.find(x => x.id === 'SP310');
console.log(strip(S.clauseDetail(c)).slice(0, 260));
console.log('\n--- index card ---');
console.log(strip(S.idxDetail(S.IDX[0])).slice(0, 160));
console.log('\n--- result row html sample ---');
const res = S.search('锂离子电池');
console.log(strip(S.resRow(res.hits[0], res.q, true)).slice(0, 200));
console.log('\n--- changelog stats ---');
console.log(JSON.stringify(S.CHG.stats, null, 1));
console.log('\n--- catalog parts/chapters ---');
S.CATALOG.parts.forEach(p => console.log('  ' + p.id + ' (' + p.chapters.length + '章): ' + p.chapters.map(c => c.id + '×' + c.count).join(' ')));
console.log('\n--- data self-consistency ---');
console.log('DGL rows', S.DGL.length, '| unique UN', new Set(S.DGL.map(r=>r.un)).size,
            '| clauses', S.CLAUSES.length, '| index', S.IDX.length,
            '| index UN not in DGL:', new Set(S.IDX.map(e=>e.un).filter(u=>!S.DGL.some(r=>r.un===u))).size);