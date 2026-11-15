// UI fixtures exercise rendering and controls; RTL correctness is tested by the Python/tool suite.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'web/index.html'), 'utf8');
const script = fs.readFileSync(path.join(root, 'web/app.js'), 'utf8');
const pipelineScript = fs.readFileSync(path.join(root, 'web/pipeline.js'), 'utf8');

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
function planFixture(body) {
  return {schema_version: 1, evidence: 'build_plan', block_id: body.lanes === 1 ? 'siliconos.matmul.serial.v1' : 'siliconos.matmul.parallel4.v1', spec: body.spec, parameters: {N: body.spec.size, LANES: body.lanes}, recipe_sha256: 'recipe' + body.lanes, source_sha256: {'hardware/matmul.sv': 'f81498d1fdb9'}, selection: 'deterministic constraint selection; no generated RTL'};
}
const settle = async () => {for (let i = 0; i < 6; i++) await new Promise(resolve => setImmediate(resolve));};
async function app(options = {}) {
  const document = documentFixture(), calls = [], routes = new Map();
  const reports = options.runs || [];
  const fetch = async (url, init = {}) => {
    const body = init.body ? JSON.parse(init.body) : undefined;
    calls.push({url, body, t: Date.now()});
    let data, ok = true;
    if (routes.has(url)) {const response = await routes.get(url)(body); data = response.data; ok = response.ok !== false;}
    else if (url === '/api/status') data = {ai: true, simulator: true, ...options.status};
    else if (url === '/api/fpga/builds') data = {builds: [buildEvidence(1), buildEvidence(4)]};
    else if (url === '/api/runs') data = reports;
    else if (url === '/api/plan') data = planFixture(body);
    else if (url === '/api/explore') data ={spec: body.spec, candidates: [1, 4].map(lanes => ({lanes, id: 'mac' + lanes, within_lane_limit: lanes <= body.spec.max_lanes, cycles: 512 / lanes, projected_us: 5.12 / lanes})), provisional: 'mac4', warning: 'Unverified resources.'};
    else throw new Error('Unconfigured fixture URL: ' + url);
    return {ok, json: async () => data, text: async () => typeof data === 'string' ? data : JSON.stringify(data)};
  };
  const context = vm.createContext({document, fetch, Blob, URL, setTimeout, matchMedia: () => ({matches: true})});
  vm.runInContext(script + '\n' + pipelineScript + '\n;globalThis.ui={state,readSpec,fillSpec,updateTarget,updateGenerateRtl,setBusy,comparable,comparison,renderResult,history,generateRtl,pipe,renderPipeline,runPipeline,showRecorded,generateSpec,useExample,checkBoardNow,diag};', context);
  await new Promise(resolve => setImmediate(resolve));
  const get = id => document.getElementById(id);
  return {ui: context.ui, get, document, routes, calls, reports, prompt(value) {get('prompt').value = value; get('prompt').oninput();}};
}

test('generation requires AI, simulator, nonempty prompt, and idle state', async () => {
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
  assert.match(a.get('generate-rtl-help').textContent, /no KV260 bitstream/);
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
  for (const result of [rtlReport({correct: false}), rtlReport({evidence: 'rtl_simulation'})]) {
    const a = await app(); a.ui.fillSpec(result.spec); a.prompt(result.prompt);
    a.routes.set('/api/generate-rtl', async () => ({data: result}));
    await a.get('generate-rtl').onclick();
    assert.equal(a.ui.state.result, null);
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

test('history retrieves the full generated report from a light summary', async () => {
  const full = rtlReport();
  const {source_files, ...summary} = full;
  const a = await app({runs: [summary]}); a.prompt(full.prompt);
  a.routes.set('/api/runs/' + full.id, async () => ({data: full}));
  assert.match(a.get('history').innerHTML, /AI-generated RTL · simulation only/);
  await a.document.querySelectorAll('[data-view]')[0].onclick();
  assert.equal(a.ui.state.result, full);
  assert.equal(a.get('stale-result').hidden, true);
});

test('the page has no ASIC target or synthesis controls', async () => {
  assert.doesNotMatch(html, /asic|yosys|generic synthesis/i);
  const a = await app();
  assert.equal(a.document.querySelectorAll('[data-target]').length, 0);
  assert.equal(a.ui.readSpec().target, 'kv260');
  assert.equal(a.get('generate-rtl').hidden, true, 'AI-written RTL is hidden in the demo');
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
  const fresh = await app({status: {board: true, board_details: {available: true, checked_at: '2026-11-15T01:20:00Z', last_check_ok: true}}});
  assert.match(fresh.get('target-state').textContent, /KV260 connected/);
  assert.equal(fresh.get('board-visual').attrs['data-state'], 'connected');
  assert.match(fresh.get('board-visual').innerHTML, /<svg class="kv260"/);
  const stale = await app({status: {board: false, board_details: {available: false, checked_at: '2026-11-15T00:00:00Z', cable_serial: 'XFL13U31JOU3A', last_check_ok: true, reason: 'last board check is 900 s old'}}});
  assert.match(stale.get('target-state').textContent, /not confirmed · last board check is 900 s old/);
  assert.equal(stale.get('board-visual').attrs['data-state'], 'unknown', 'a stale passing check is drawn neither as connected nor as a fault');
  const noCable = await app({status: {board: false, board_details: {available: false, checked_at: '2026-11-15T01:20:00Z', cable_serial: null, last_check_ok: false, reason: 'no JTAG cable'}}});
  assert.equal(noCable.get('board-visual').attrs['data-state'], 'unplugged');
  const noAnswer = await app({status: {board: false, board_details: {available: false, checked_at: '2026-11-15T01:20:00Z', cable_serial: 'XFL13U31JOU3A', last_check_ok: false, reason: 'board not detected'}}});
  assert.equal(noAnswer.get('board-visual').attrs['data-state'], 'nopower');
  const none = await app();
  assert.match(none.get('target-state').textContent, /not checked/);
});

const RTL = 'f81498d1fdb9a73a32e7f70a5d55c09b6198d2f03f00ab27d9099a63d82f418c';
function buildEvidence(lanes, overrides = {}) {
  return {lanes, N: 8, vivado: '2025.2', part: 'xck26-sfvc784-2LV-c', build_started_at: '2026-11-14T15:43:04-08:00', build_minutes: 10.2, rtl_sha256: {'matmul.sv': RTL}, rtl_matches_app: true, bitstream: `matmul_board_n8_l${lanes}.bit`, bitstream_sha256: 'bit' + lanes, bitstream_verified: true, configured_clock_hz: 99999001, timing: {met: true, WNS_ns: lanes === 1 ? 4.757 : 3.885, WHS_ns: 0.001, fmax_estimate_mhz: lanes === 1 ? 190.7 : 163.5, kernel_worst_path: {slack_ns: 4.9, source: 'k_reg', destination: 'acc_reg', logic_levels: 13}}, area: {'Total LUTs': lanes === 1 ? 354 : 3612, FFs: lanes === 1 ? 318 : 2470, 'DSP Blocks': 0, RAMB36: 0, RAMB18: 0}, area_scope: 'instance u_matmul (matmul_axi)', power: {kernel_w: 0.002, total_w: 2.723}, drc_clean: true, synthesis: {rtl_components: [{category: 'Adders', item: '2 Input 32 Bit Adders', count: 5}]}, reports: [{name: 'timing_summary.rpt', verified: true}, {name: 'utilization.rpt', verified: true}, {name: 'power.rpt', verified: true}], ...overrides};
}
function simRun(lanes, overrides = {}) {
  return rtlReport({id: 'sim-' + lanes, evidence: 'rtl_simulation', prompt: undefined, lanes, cycles: 512 / lanes, outputs: Array(64).fill(7), source_sha256: {'matmul.sv': RTL, 'tb.sv': 'tb'}, input_sha256: 'same-inputs', simulator_stdout: 'CYCLES ' + 512 / lanes + '\nOUT 7', ...overrides});
}
const TIMING_RPT = ['| Design Timing Summary', '| ---------------------', '-----', '', '    WNS(ns)      TNS(ns)', '    -------      -------', '      4.757        0.000', '', '', 'All user specified timing constraints are met.'].join('\n');
const XSDB_LOG = ['MM BEGIN n=8 base=0xA0000000', 'MM ID 1397312513', 'MM JOB first status=2 polls=0 timeout=0 cycles_lo=512 cycles_hi=0 host_ns=810362000', 'MM OUT first ' + Array(64).fill(7).join(' '), 'MM END'].join('\n');
function pipelineApp(a, {check = {available: true, checked_at: '2026-11-15T06:00:00Z', cable_serial: 'XFL13U31JOU3A', devices: ['1  Xilinx X-MLCC-01 XFL13U31JOU3A', '2  xck26 (idcode 04724093 irlen 12 fpga)', '3  arm_dap (idcode 5ba00477 irlen 4)']}, builds} = {}) {
  a.routes.set('/api/simulate', async body => ({data: simRun(body.lanes, {spec: body.spec})}));
  for (const lanes of [1, 4]) {
    const folder = `20261115T06000${lanes}Z_n8_l${lanes}`;
    a.routes.set(`/api/runs/sim-${lanes}/handoff.json`, async () => ({data: {files: [{name: 'hardware/matmul.sv', sha256: RTL}, {name: 'manifest.json', sha256: null}]}}));
    a.routes.set(`/api/runs/sim-${lanes}/board-run`, async () => ({data: {id: 'job-' + lanes, status: 'done', stage: 'done', child_id: 'board-' + lanes, zip_sha256: 'zip' + lanes, result_folder: folder, log: []}}));
    a.routes.set('/api/runs/board-' + lanes, async () => ({data: boardReport(lanes, {runner_result_folder: folder, interface_check: {identity: 1397312513, compiled_n: 8, compiled_lanes: lanes, base_address: '0xA0000000'}})}));
    a.routes.set(`/api/fpga/builds/${lanes}/reports/timing_summary.rpt`, async () => ({data: TIMING_RPT}));
    a.routes.set(`/api/board/results/${folder}/xsdb.log`, async () => ({data: XSDB_LOG}));
  }
  a.routes.set('/api/board/check', async () => ({data: check}));
  if (builds) a.routes.set('/api/fpga/builds', async () => ({data: {builds}}));
  return a;
}
const flowHtml = a => ['art-rtl', 'art-vivado', 'art-board', 'art-results'].map(id => a.get(id).innerHTML).join('\n');
const called = (a, url) => a.calls.some(call => call.url === url);

test('the AI spec appears with both architectures, and nothing runs until Build is clicked', async () => {
  const a = pipelineApp(await app());
  a.routes.set('/api/spec', async body => ({data: {supported: true, explanation: 'Supported 8x8 INT8 GEMM.', spec: {...spec}, provenance: {size: 'user', max_lanes: 'user'}, unresolved: []}}));
  assert.equal(a.get('step-spec').hidden, true);
  a.prompt('Fast 8x8 INT8 matmul on the KV260');
  a.ui.state.aiDetails = {model: 'openai/gpt-oss-20b'};
  await a.ui.generateSpec();
  assert.equal(a.get('step-spec').hidden, false);
  assert.equal(a.ui.state.specOrigin.kind, 'ai');
  assert.match(a.get('spec-origin').textContent, /Drafted by AI \(openai\/gpt-oss-20b\)/);
  assert.match(a.get('spec-notes').innerHTML, /Fast 8x8 INT8 matmul on the KV260/);
  assert.match(a.get('arch-view').innerHTML, /1 lane · Sequential MAC/);
  assert.match(a.get('arch-view').innerHTML, /4 lanes · Parallel MAC array/);
  assert.match(a.get('arch-view').innerHTML, /KV260 bitstream ready/);
  assert.equal(called(a, '/api/simulate'), false);
  assert.equal(a.get('step-rtl').hidden, true);
  a.routes.set('/api/spec', async () => ({data: {supported: false, explanation: 'Camera inference is unsupported.', spec: {...spec}, provenance: {}, unresolved: []}}));
  const b = pipelineApp(await app());
  b.routes.set('/api/spec', async () => ({data: {supported: false, explanation: 'Camera inference is unsupported.', spec: {...spec}, provenance: {}, unresolved: []}}));
  b.prompt('detect cats on a camera');
  await b.ui.generateSpec();
  assert.equal(b.get('step-spec').hidden, true);
  assert.match(b.get('notice').textContent, /Camera inference is unsupported/);
});

test('Build runs every step in order and shows each step\'s artifacts and a 1 vs 4 lane chart', async () => {
  const a = pipelineApp(await app());
  a.ui.fillSpec({...spec}, {size: 'user'}, {kind: 'ai', prompt: 'Fast 8x8 INT8 matmul on the KV260', model: 'openai/gpt-oss-20b'});
  await a.ui.runPipeline();
  for (const step of ['sim', 'handoff', 'vivado', 'board', 'run', 'import', 'compare']) assert.equal(a.ui.pipe.status[step], 'done', step);
  const urls = a.calls.map(c => c.url), rtlEnd = urls.lastIndexOf('/api/runs/sim-4/handoff.json'), vivadoStart = urls.indexOf('/api/fpga/builds', rtlEnd);
  const vivadoEnd = urls.lastIndexOf('/api/fpga/builds/4/reports/timing_summary.rpt'), boardStart = urls.indexOf('/api/board/check');
  assert.ok(a.calls[vivadoStart].t - a.calls[rtlEnd].t >= 950, 'the finished RTL step stays on screen ~1 s before Vivado starts');
  assert.ok(a.calls[boardStart].t - a.calls[vivadoEnd].t >= 950, 'the finished Vivado step stays on screen ~1 s before the board check');
  for (const id of ['step-spec', 'step-diagram', 'step-rtl', 'step-vivado', 'step-board', 'step-results']) assert.equal(a.get(id).hidden, false, id);
  assert.match(a.get('flow-progress').innerHTML, /class="done"><a href="#step-results"><b>✓<\/b>Results/);
  assert.match(a.get('art-rtl').innerHTML, /hardware\/matmul\.sv/);
  assert.match(a.get('art-rtl').innerHTML, /64\/64 ✓/);
  assert.match(a.get('art-vivado').innerHTML, /reused, not rebuilt/);
  assert.match(a.get('art-vivado').innerHTML, /All user specified timing constraints are met\./);
  assert.match(a.get('art-vivado').innerHTML, /\/api\/fpga\/builds\/1\/reports\/timing_summary\.rpt/);
  assert.match(a.get('board-side').innerHTML, /KV260 connected/);
  assert.equal(a.get('board-visual-big').attrs['data-state'], 'connected');
  assert.equal(a.get('board-scene').attrs['data-state'], 'connected');
  for (const node of ['XFL13U31JOU3A', 'xck26', 'arm_dap']) assert.match(a.get('board-side').innerHTML, new RegExp(`<li class="ok">((?!</li>).)*${node}`), node);
  assert.equal(a.ui.state.boardActivity, null, 'the sidebar returns to the check result after the run');
  assert.match(a.get('art-board').innerHTML, /MM JOB first status=2/);
  assert.match(a.get('art-board').innerHTML, /\(64 values\)/);
  assert.match(a.get('art-board').innerHTML, /Identity register 0x53494C01/);
  assert.match(a.get('art-board').innerHTML, /\/api\/board\/results\/20261115T060001Z_n8_l1\/xsdb\.log/);
  const results = a.get('art-results').innerHTML;
  assert.match(results, /<strong>4\.00×<\/strong><span>fewer kernel cycles, measured on the KV260/);
  assert.match(results, /<strong>10\.2×<\/strong>/);
  assert.match(results, /Kernel cycles · measured on the KV260/);
  assert.match(results, /Matmul LUTs/);
  assert.match(results, /not a stopwatch time/);
  assert.match(a.get('live-final').innerHTML, /Pipeline complete/);
  assert.equal(a.ui.state.busy, false);
});

test('Build stops before programming when the board is not detected', async () => {
  const a = pipelineApp(await app(), {check: {available: false, reason: 'board not detected', devices: []}});
  await a.ui.runPipeline();
  assert.equal(a.ui.pipe.status.board, 'failed');
  assert.notEqual(a.ui.pipe.status.run, 'done');
  assert.equal(called(a, '/api/runs/sim-1/board-run'), false);
  assert.match(a.get('art-board').innerHTML, /J4/);
  assert.equal(a.get('board-visual-big').attrs['data-state'], 'unplugged');
  assert.match(a.get('board-side').innerHTML, /USB-JTAG cable not found/);
  assert.match(a.get('board-side').innerHTML, /<li class="miss">((?!<\/li>).)*USB-JTAG cable/);
  assert.equal(a.get('step-results').hidden, true);
  assert.equal(a.get('notice').className, 'notice error');
});

test('a cable without a responding board points at power (J12), not the cable', async () => {
  const a = pipelineApp(await app(), {check: {available: false, cable_serial: 'XFL13U31JOU3A', devices: ['1  Xilinx X-MLCC-01 XFL13U31JOU3A'], reason: 'board not detected: need a JTAG cable with xck26 and arm_dap devices'}});
  await a.ui.runPipeline();
  assert.equal(a.ui.pipe.status.board, 'failed');
  assert.equal(called(a, '/api/runs/sim-1/board-run'), false);
  assert.equal(a.get('board-visual-big').attrs['data-state'], 'nopower');
  const side = a.get('board-side').innerHTML;
  assert.match(side, /J12/);
  assert.match(side, /<li class="ok">((?!<\/li>).)*XFL13U31JOU3A/);
  assert.match(side, /<li class="miss">((?!<\/li>).)*xck26/);
  assert.match(side, /<li class="miss">((?!<\/li>).)*arm_dap/);
});

test('Check board animates a scan, then shows the board plugged in', async () => {
  const a = pipelineApp(await app());
  assert.equal(a.get('board-visual').attrs['data-state'], 'unknown');
  const pending = a.ui.checkBoardNow();
  assert.equal(a.get('board-visual').attrs['data-state'], 'checking');
  assert.match(a.get('target-state').textContent, /Scanning JTAG/);
  await pending;
  assert.equal(a.get('board-visual').attrs['data-state'], 'connected');
  assert.equal(a.get('target-state').attrs['data-state'], 'connected');
  assert.match(a.get('target-state').textContent, /KV260 connected/);
  assert.equal(called(a, '/api/runs/sim-1/board-run'), false, 'a check never programs the board');
});

test('the block diagram is developed from the validated plan after the spec and before any RTL runs', async () => {
  const a = pipelineApp(await app());
  a.routes.set('/api/spec', async () => ({data: {supported: true, explanation: 'Supported 8x8 INT8 GEMM.', spec: {...spec}, provenance: {size: 'user'}, unresolved: []}}));
  assert.equal(a.get('step-diagram').hidden, true);
  a.prompt('Fast 8x8 INT8 matmul on the KV260');
  await a.ui.generateSpec();
  await settle();
  assert.equal(a.get('step-diagram').hidden, false);
  assert.deepEqual([...new Set(a.calls.filter(c => c.url === '/api/plan').map(c => c.body.lanes))].sort(), [1, 4]);
  const four = a.get('art-diagram').innerHTML;
  assert.match(four, /siliconos\.matmul\.parallel4\.v1/);
  assert.match(four, /CONCEPTUAL · NOT VIVADO/);
  assert.match(four, /MAC 4/);
  assert.match(four, /RTL DATA PATH \/ 8 × 8/);
  assert.match(four, /32-bit acc/);
  assert.match(four, /not a BRAM mapping claim/);
  assert.match(four, /Zynq PS → AXI4-Lite → matmul_axi/);
  assert.match(four, /0xA0000000/);
  assert.match(a.get('flow-progress').innerHTML, /class="done"><a href="#step-diagram"><b>✓<\/b>Block diagram/);
  assert.equal(called(a, '/api/simulate'), false, 'the diagram is a plan; nothing runs until Build');
  assert.equal(a.get('step-rtl').hidden, true);
  await a.document.querySelector('[data-diagram="1"]').onclick();
  const one = a.get('art-diagram').innerHTML;
  assert.match(one, /siliconos\.matmul\.serial\.v1/);
  assert.match(one, /LANES=1/);
  assert.doesNotMatch(one, /MAC 2/);
});

test('a 16 x 16 block diagram does not claim a KV260 bitstream', async () => {
  const a = pipelineApp(await app());
  await a.ui.useExample();
  a.get('size').value = '16';
  a.get('size').onchange();
  await settle();
  const html = a.get('art-diagram').innerHTML;
  assert.match(html, /RTL DATA PATH \/ 16 × 16/);
  assert.match(html, /SIMULATION ONLY/);
  assert.doesNotMatch(html, /0xA0000000/);
});

test('a rejected plan shows a visible block diagram error instead of a diagram', async () => {
  const a = pipelineApp(await app());
  a.routes.set('/api/plan', async () => ({ok: false, data: {error: 'Unsupported catalog lane configuration.'}}));
  await a.ui.useExample();
  await settle();
  assert.equal(a.ui.diag.status, 'failed');
  assert.match(a.get('art-diagram').innerHTML, /Block diagram unavailable: Unsupported catalog lane configuration\./);
  assert.doesNotMatch(a.get('art-diagram').innerHTML, /RTL DATA PATH/);
  assert.match(a.get('flow-progress').innerHTML, /class="failed"><a href="#step-diagram">/);
});

test('Build refuses a bitstream that was not built from the simulated RTL', async () => {
  const a = pipelineApp(await app(), {builds: [buildEvidence(1, {rtl_sha256: {'matmul.sv': 'other'}}), buildEvidence(4)]});
  await a.ui.runPipeline();
  assert.equal(a.ui.pipe.status.vivado, 'failed');
  assert.equal(called(a, '/api/board/check'), false);
  assert.match(a.get('art-vivado').innerHTML, /not built from this RTL/);
  assert.equal(a.get('step-board').hidden, true);
});

test('16 x 16 runs stop after simulation and never touch the board', async () => {
  const a = pipelineApp(await app());
  a.get('size').value = '16';
  await a.ui.runPipeline();
  assert.equal(a.ui.pipe.status.sim, 'done');
  for (const step of ['vivado', 'board', 'run', 'import']) assert.equal(a.ui.pipe.status[step], 'skipped', step);
  assert.equal(called(a, '/api/board/check'), false);
  assert.match(a.get('art-vivado').innerHTML, /built for 8 × 8 only/);
  assert.doesNotMatch(flowHtml(a), /measured on the KV260/);
});

test('the recorded run is labelled as recorded, not live', async () => {
  const one = boardReport(1, {parent_run_id: 'sim-1'}), four = boardReport(4, {parent_run_id: 'sim-4'});
  const a = pipelineApp(await app({runs: [four, one]}));
  a.routes.set('/api/runs/board-1', async () => ({data: one}));
  a.routes.set('/api/runs/board-4', async () => ({data: four}));
  a.routes.set('/api/runs/sim-1', async () => ({data: simRun(1)}));
  a.routes.set('/api/runs/sim-4', async () => ({data: simRun(4)}));
  await a.ui.showRecorded();
  assert.match(a.get('live-final').innerHTML, /Recorded real run \(not live\)/);
  assert.equal(a.get('board-visual-big').attrs['data-state'], 'recorded');
  assert.match(a.get('board-side').innerHTML, /Recorded KV260 run \(not live\)/);
  assert.match(a.get('art-results').innerHTML, /fewer kernel cycles, measured on the KV260/);
  assert.equal(called(a, '/api/board/check'), false);
});
