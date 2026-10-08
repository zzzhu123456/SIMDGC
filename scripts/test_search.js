global.window = {};
global.atob = s => Buffer.from(s, 'base64').toString('binary');
const stubEl = () => ({
  innerHTML: '', textContent: '', value: '', dataset: {},
  classList: { add() {}, remove() {}, toggle() {} },
  querySelectorAll: () => [], querySelector: () => null,
  addEventListener() {}, onclick: null
});
global.document = { getElementById: () => stubEl(), querySelectorAll: () => [], addEventListener: () => {} };
const fs = require('fs');
for (const n of ['catalog', 'dgl', 'clauses', 'idx', 'changelog', 'sindex']) {
  eval(fs.readFileSync('web/data/' + n + '.js', 'utf8'));
}
eval(fs.readFileSync('web/app.js', 'utf8'));
const S = window.__IMDG;
const show = (q, n) => {
  const t0 = Date.now();
  const r = S.search(q);
  const ms = Date.now() - t0;
  console.log('\n=== ' + q + '  ->  mode=' + r.q.mode + '  hits=' + r.hits.length + '  ' + ms + 'ms');
  r.hits.slice(0, n || 4).forEach(h => console.log('   [' + h.d.k + '] ' + h.d.title.slice(0, 62) + '  |  ' + h.d.sub.slice(0, 34) + '  p.' + h.d.page));
};
show('1203');
show('UN 3082');
show('锂离子电池', 5);
show('SP310');
show('P001', 3);
show('7.1.5', 3);
show('SGG2', 3);
show('隔离');
show('钠离子');
show('灭火剂分散装置');
show('3560');
show('积载类E', 3);
show('海洋污染物', 3);
show('包装导则', 3);
show('IBC02');
show('T4', 3);
console.log('\ntokenize("锂离子电池"):', S.tokenize('锂离子电池'));
console.log('normalize("第1.1 章 UN 1203 车用汽油"):', S.normalize('第1.1 章 UN 1203 车用汽油'));