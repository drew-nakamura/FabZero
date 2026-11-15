// UI fixtures exercise rendering and controls; RTL correctness is tested by the Python/tool suite.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'web/index.html'), 'utf8');
const script = fs.readFileSync(path.join(root, 'web/app.js'), 'utf8');

class Element {
  constructor(tag, attrs = {}) {
    this.tagName = tag; this.attrs = attrs; this.id = attrs.id;
    this.className = attrs.class || ''; this.value = attrs.value || '';
    this.disabled = 'disabled' in attrs; this.hidden = 'hidden' in attrs;
    this.dataset = Object.fromEntries(Object.entries(attrs).filter(([key]) => key.startsWith('data-')).map(([key, value]) => [key.slice(5), value]));
    this.children = []; this.valid = true; this.textContent = '';
    this.classList = {toggle: (name, active) => {const classes = new Set(this.className.split(' ')); active ? classes.add(name) : classes.delete(name); this.className = [...classes].join(' ');}};
  }
  set innerHTML(value) {this._html = value; this.children = parse(value);}
  get innerHTML() {return this._html || '';}
  setAttribute(key, value) {this.attrs[key] = value;}
  reportValidity() {return this.valid;}
  scrollIntoView() {}
  querySelector(selector) {return flatten(this.children).find(element => matches(element, selector)) || null;}
}
function parse(markup) {
  const elements = [], ancestors = [], voidTags = new Set(['input', 'br', 'hr', 'meta', 'link', 'img']);
  for (const [, closing, tag, raw] of markup.matchAll(/<(\/?)([a-z][\w-]*)\b([^>]*)>/gi)) {
    if (closing) {const at = ancestors.findLastIndex(element => element.tagName === tag); if (at >= 0) ancestors.splice(at); continue;}
    const attrs = Object.fromEntries([...raw.matchAll(/([\w-]+)(?:="([^"]*)")?/g)].map(([, key, value]) => [key, value || '']));
    const element = new Element(tag, attrs);
    element.inBuilder = ancestors.some(parent => parent.className.split(' ').includes('builder'));
    elements.push(element); if (!voidTags.has(tag)) ancestors.push(element);
  }
  return elements;
}
function flatten(nodes) {return nodes.flatMap(node => [node, ...flatten(node.children)]);}
function matches(element, selector) {
  selector = selector.trim();
  if (selector.startsWith('.builder ')) return element.inBuilder && matches(element, selector.slice(9));
  if (selector.startsWith('.')) return element.className.split(' ').includes(selector.slice(1));
  const attr = selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);
  if (attr) return attr[1] in element.attrs && (attr[2] === undefined || element.attrs[attr[1]] === attr[2]);
  return element.tagName === selector;
}
function documentFixture() {
  const nodes = parse(html);
  const document = {
    getElementById: id => flatten(nodes).find(element => element.id === id) || null,
    querySelectorAll: selector => flatten(nodes).filter(element => selector.split(',').some(part => matches(element, part))),
    querySelector: selector => document.querySelectorAll(selector)[0] || null,
    createElement: tag => new Element(tag),
  };
  document.getElementById('size').value = '8';
  document.getElementById('max_lanes').value = '4';
  document.getElementById('objective').value = 'minimize_latency';
  return document;
}
const spec = {operation: 'matrix_multiply', size: 8, precision: 'int8', target: 'kv260', frequency_mhz: 100, max_dsps: 16, max_lanes: 4, objective: 'minimize_latency'};
function rtlReport(overrides = {}) {
  return {id: 'fixture-run', created_at: '2026-11-14T00:00:00Z', evidence: 'ai_generated_rtl', correct: true, spec: {...spec}, lanes: 4, seed: 42, prompt: 'Multiply signed INT8 matrices', cycles: 129, projected_us: 1.29, outputs: [123], limitations: ['UI fixture only'], simulator: 'Icarus fixture', source_sha256: {'matmul.sv': 'generated-fixture-hash', 'tb.sv': 'testbench-fixture-hash'}, input_sha256: 'input-fixture-hash', output_sha256: 'output-fixture-hash', source_files: {'matmul.sv': 'verified-fixture-source'}, ...overrides};
}
function asicReport(overrides = {}) {
  return {evidence: 'generic_synthesis', source_origin: 'ai_generated_rtl', correct: true, spec: {...spec, target: 'asic'}, lanes: 4, cell_count: 123, cell_counts: {'$add': 4}, limitations: ['UI fixture only'], netlist_verilog: 'netlist-fixture', synthesis_script: 'script-fixture', ...overrides};
}
async function app(options = {}) {
  const document = documentFixture(), calls = [], routes = new Map();
  const reports = options.runs || [];
  const fetch = async (url, init = {}) => {
    const body = init.body ? JSON.parse(init.body) : undefined;
    calls.push({url, body});
    let data, ok = true;
    if (routes.has(url)) {const response = await routes.get(url)(body); data = response.data; ok = response.ok !== false;}
    else if (url === '/api/status') data = {ai: true, simulator: true, asic_synthesis: true, ...options.status};
    else if (url === '/api/runs') data = reports;
    else if (url === '/api/explore') data = {spec: body.spec, candidates: [1, 4].map(lanes => ({lanes, id: 'mac' + lanes, within_lane_limit: lanes <= body.spec.max_lanes, cycles: 512 / lanes, projected_us: 5.12 / lanes})), provisional: 'mac4', warning: 'Unverified resources.'};
    else throw new Error('Unconfigured fixture URL: ' + url);
    return {ok, json: async () => data};
  };
  const context = vm.createContext({document, fetch, Blob, URL, setTimeout, matchMedia: () => ({matches: true})});
  vm.runInContext(script + '\n;globalThis.ui={state,readSpec,fillSpec,updateTarget,updateGenerateRtl,setBusy,comparable,comparison,renderResult,renderSynthesis,history,generateRtl};', context);
  await new Promise(resolve => setImmediate(resolve));
  const get = id => document.getElementById(id);
  return {ui: context.ui, get, document, routes, calls, reports, prompt(value) {get('prompt').value = value; get('prompt').oninput();}};
}

test('generation requires AI, simulator, nonempty prompt, idle state, and synthesis for ASIC', async () => {
  const a = await app();
  assert.equal(a.get('generate-rtl').disabled, true);
  a.prompt('   '); assert.equal(a.get('generate-rtl').disabled, true);
  a.prompt('Multiply signed INT8 matrices'); assert.equal(a.get('generate-rtl').disabled, false);
  for (const key of ['ai', 'simulator']) {
    a.ui.state[key] = false; a.ui.updateGenerateRtl();
    assert.equal(a.get('generate-rtl').disabled, true);
    await a.ui.generateRtl(); assert.equal(a.calls.some(call => call.url === '/api/generate-rtl'), false);
    a.ui.state[key] = true;
  }
  a.ui.state.asicSynthesis = false; a.ui.updateGenerateRtl();
  assert.equal(a.get('generate-rtl').disabled, false, 'FPGA does not require Yosys');
  a.ui.state.spec.target = 'asic'; a.ui.updateTarget();
  assert.equal(a.get('generate-rtl').disabled, true);
  assert.match(a.get('generate-rtl-help').textContent, /Requires Yosys synthesis/);
  a.ui.state.asicSynthesis = true; a.ui.updateGenerateRtl();
  assert.equal(a.get('generate-rtl').disabled, false);
  a.ui.setBusy(true); assert.equal(a.get('generate-rtl').disabled, true);
  a.ui.setBusy(false); assert.equal(a.get('generate-rtl').disabled, false);
  a.get('objective').value = 'minimize_lanes'; a.get('objective').oninput();
  assert.match(a.get('generate-rtl-help').textContent, /1 requested lane\./);
});

test('one click sends the reviewed spec and prompt, then renders verified generated evidence', async () => {
  const a = await app(), result = rtlReport(); a.prompt(result.prompt);
  a.routes.set('/api/generate-rtl', async body => {
    assert.deepEqual(body, {spec, prompt: result.prompt});
    assert.equal(a.get('generate-rtl').disabled, true);
    a.reports.push(result); return {data: result};
  });
  await a.get('generate-rtl').onclick();
  assert.equal(a.ui.state.result.id, result.id);
  assert.match(a.get('result').innerHTML, /AI-generated RTL, verified by simulation against an integer oracle/);
  assert.match(a.get('result').innerHTML, /Checked-in architecture projections do not describe this generated schedule/);
  assert.match(a.get('history').innerHTML, /AI-generated RTL/);
  assert.equal(a.get('stale-result').hidden, true);
  assert.equal(a.get('generate-rtl').disabled, false);
  assert.equal(a.ui.state.busy, false);
  assert.equal(a.get('export').disabled, false);
});

test('ASIC completion labels synthesis separately and both reports become stale on prompt or spec edits', async () => {
  const a = await app(), result = rtlReport({spec: {...spec, target: 'asic'}, synthesis: asicReport(), synthesis_verified: true});
  a.ui.fillSpec(result.spec); a.prompt(result.prompt);
  a.routes.set('/api/generate-rtl', async () => ({data: result}));
  await a.get('generate-rtl').onclick();
  assert.equal(a.ui.state.synthesis, result.synthesis);
  assert.match(a.get('synthesis-result').innerHTML, /GENERIC SYNTHESIS · NOT A PHYSICAL CHIP/);
  assert.match(a.get('synthesis-result').innerHTML, /Source: AI-generated RTL, verified by simulation against an integer oracle/);
  assert.match(a.get('synthesis-result').innerHTML, /not standard-cell area/);
  assert.equal(a.get('stale-result').hidden, true);
  assert.equal(a.get('stale-synthesis').hidden, true);
  assert.equal(a.get('export-netlist').disabled, false);
  a.prompt(result.prompt + ' changed');
  assert.equal(a.get('stale-result').hidden, false);
  assert.equal(a.get('stale-synthesis').hidden, false);
  a.prompt(result.prompt);
  assert.equal(a.get('stale-synthesis').hidden, true);
  a.get('size').value = '16'; a.get('size').oninput();
  assert.equal(a.get('stale-result').hidden, false);
  assert.equal(a.get('stale-synthesis').hidden, false);
});

test('rejection preserves prior verified evidence and reports an honest visible error', async () => {
  const a = await app(), prior = rtlReport({id: 'prior-verified'});
  a.prompt(prior.prompt); a.ui.renderResult(prior);
  const previous = a.get('result').innerHTML;
  a.routes.set('/api/generate-rtl', async () => ({ok: false, data: {error: 'Generated RTL compilation failed; no result accepted.'}}));
  await a.get('generate-rtl').onclick();
  assert.equal(a.get('result').innerHTML, previous);
  assert.equal(a.ui.state.result.id, 'prior-verified');
  assert.match(a.get('notice').textContent, /compilation failed/);
  assert.match(a.get('notice').textContent, /previously verified report remains displayed/);
  assert.equal(a.get('notice').className, 'notice error');
  assert.equal(a.get('generate-rtl').disabled, false);
});

test('unverified or incomplete successful responses never replace accepted evidence', async () => {
  for (const result of [rtlReport({correct: false}), rtlReport({evidence: 'rtl_simulation'}), rtlReport({spec: {...spec, target: 'asic'}})]) {
    const a = await app(); a.ui.fillSpec(result.spec); a.prompt(result.prompt);
    a.routes.set('/api/generate-rtl', async () => ({data: result}));
    await a.get('generate-rtl').onclick();
    assert.equal(a.ui.state.result, null);
    assert.equal(a.ui.state.synthesis, null);
    assert.match(a.get('notice').textContent, /did not return a fully verified/);
    assert.equal(a.get('export').disabled, true);
  }
});

test('comparisons require identical evidence origin and source hashes', async () => {
  const a = await app(), generated = rtlReport(), other = rtlReport({lanes: 1, cycles: 513});
  assert.equal(a.ui.comparable(generated, other), true);
  assert.equal(a.ui.comparable(generated, {...other, evidence: 'rtl_simulation'}), false);
  assert.equal(a.ui.comparable(generated, {...other, source_sha256: {'matmul.sv': 'different'}}), false);
  assert.equal(a.ui.comparable(generated, {...other, input_sha256: 'different'}), false);
  assert.equal(a.ui.comparable(generated, {...other, correct: false}), false);
  a.ui.state.runs = [{...other, evidence: 'rtl_simulation'}];
  assert.doesNotMatch(a.ui.comparison(generated), /simulated kernel speedup/);
  a.ui.state.runs = [other];
  assert.match(a.ui.comparison(generated), /MATCHED AI RTL SIMULATION COMPARISON/);
  assert.match(a.ui.comparison(generated), /physical resource usage remains unknown/);
});

test('history retrieves the full generated report and nested synthesis from a light summary', async () => {
  const full = rtlReport({spec: {...spec, target: 'asic'}, synthesis: asicReport(), synthesis_verified: true});
  const {synthesis, source_files, ...summary} = full;
  const a = await app({runs: [summary]}); a.prompt(full.prompt);
  a.routes.set('/api/runs/' + full.id, async () => ({data: full}));
  assert.match(a.get('history').innerHTML, /AI-generated RTL · generic synthesis verified/);
  await a.document.querySelectorAll('[data-view]')[0].onclick();
  assert.equal(a.ui.state.result, full);
  assert.equal(a.ui.state.synthesis, full.synthesis);
  assert.equal(a.get('asic-stage').hidden, false);
  assert.equal(a.get('stale-synthesis').hidden, true);
});

test('curated reports stay distinct and prompt edits do not make them stale', async () => {
  const a = await app(), curated = rtlReport({evidence: 'rtl_simulation', prompt: undefined});
  a.ui.renderResult(curated); a.prompt('new generated workload');
  assert.equal(a.get('stale-result').hidden, true);
  assert.match(a.get('result').innerHTML, /CHECKED-IN RTL SIMULATION/);
  assert.doesNotMatch(a.get('result').innerHTML, /AI-generated RTL, verified by simulation/);
  a.get('size').value = '16'; a.get('size').oninput();
  assert.equal(a.get('stale-result').hidden, false);
});

test('example prompt buttons enable generation and mark generated evidence stale', async () => {
  const a = await app(), result = rtlReport(); a.prompt(result.prompt); a.ui.renderResult(result);
  a.document.querySelectorAll('[data-example]')[0].onclick();
  assert.equal(a.get('generate-rtl').disabled, false);
  assert.equal(a.get('stale-result').hidden, false);
});


test('history refresh failure preserves successful generation without falsely reporting rejection', async () => {
  const a = await app(), result = rtlReport(); a.prompt(result.prompt);
  a.routes.set('/api/generate-rtl', async () => ({data: result}));
  a.routes.set('/api/runs', async () => ({ok: false, data: {error: 'History temporarily unavailable'}}));
  await a.get('generate-rtl').onclick();
  assert.equal(a.ui.state.result, result);
  assert.match(a.get('notice').textContent, /Generated RTL verification passed/);
  assert.match(a.get('notice').textContent, /history could not be refreshed/);
  assert.doesNotMatch(a.get('notice').textContent, /generation rejected|previously verified/);
  assert.equal(a.get('export').disabled, false);
});

function boardReport(lanes, overrides = {}) {
  return {id: 'board-' + lanes, created_at: '2026-11-15T01:20:00Z', recorded_at: '2026-11-14T17:20:00-08:00', evidence: 'board_measured', correct: true, physical_fpga: true, parent_run_id: 'parent-' + lanes, runner_result_id: 'runner-result-' + lanes, spec: {...spec}, lanes, cycles: 512 / lanes, kernel_time_us: 5.12 / lanes, configured_clock_hz: 99999001, outputs: Array(64).fill(1), input_sha256: 'same-inputs', host_elapsed_ns: 6.3e9, programming_elapsed_ns: 5.7e9, build: {bitstream_sha256: 'abcdef0123456789', timing: {WNS_ns: 4.757}}, resources: {'Total LUTs': lanes === 1 ? 354 : 3612, FFs: 318, 'DSP Blocks': 0, RAMB36: 0}, board_import: {key_id: 'fixture-key'}, limitations: ['Board fixture only'], ...overrides};
}

test('board-measured runs render as physical evidence with a measured lane comparison', async () => {
  const a = await app(), one = boardReport(1), four = boardReport(4);
  a.ui.state.runs = [one, four];
  a.ui.renderResult(four);
  const html = a.get('result').innerHTML;
  assert.match(html, /PHYSICAL FPGA · BOARD MEASURED/);
  assert.match(html, /MEASURED KERNEL CYCLES/);
  assert.match(html, /4\.00× fewer kernel cycles/);
  assert.match(html, /10\.2× the matmul LUTs/);
  assert.match(html, /not a measured time/);
  assert.doesNotMatch(html, /NOT HARDWARE MEASURED/);
  assert.equal(a.ui.state.result, four);
});

test('simulation results link to their board runs and offer the FPGA handoff ZIP', async () => {
  const a = await app(), sim = rtlReport({id: 'parent-1', evidence: 'rtl_simulation', lanes: 1});
  a.ui.state.runs = [];
  a.ui.renderResult(sim);
  assert.match(a.get('result').innerHTML, /Not yet run on the KV260/);
  assert.match(a.get('result').innerHTML, /\/api\/runs\/parent-1\/handoff\.zip/);
  a.ui.state.runs = [boardReport(1)];
  a.ui.renderResult(sim);
  assert.match(a.get('result').innerHTML, /Measured on the KV260 · 512 cycles/);
});

test('board status is shown only from a fresh passing check', async () => {
  const fresh = await app({status: {board: true, board_details: {available: true, checked_at: '2026-11-15T01:20:00Z'}}});
  assert.match(fresh.get('target-state').textContent, /KV260 connected/);
  const stale = await app({status: {board: false, board_details: {available: false, checked_at: '2026-11-15T00:00:00Z', reason: 'last board check is 900 s old'}}});
  assert.match(stale.get('target-state').textContent, /not confirmed · last board check is 900 s old/);
  const none = await app();
  assert.match(none.get('target-state').textContent, /not checked/);
});
