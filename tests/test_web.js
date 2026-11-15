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
    this.children = []; this.valid = true; this.textContent = ''; this.files = [];
    this.clicked = false;
    this.classList = {toggle: (name, active) => {const classes = new Set(this.className.split(' ')); active ? classes.add(name) : classes.delete(name); this.className = [...classes].join(' ');}};
  }
  set innerHTML(value) {this._html = value; this.children = parse(value);}
  get innerHTML() {return this._html || '';}
  setAttribute(key, value) {this.attrs[key] = value;}
  reportValidity() {return this.valid;}
  scrollIntoView() {}
  click() {this.clicked = true; if (this.onclick) return this.onclick();}
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
  const nodes = parse(html), created = [];
  const document = {
    getElementById: id => flatten(nodes).find(element => element.id === id) || null,
    querySelectorAll: selector => flatten(nodes).filter(element => selector.split(',').some(part => matches(element, part))),
    querySelector: selector => document.querySelectorAll(selector)[0] || null,
    createElement: tag => {const element = new Element(tag); created.push(element); return element;},
    created,
  };
  document.getElementById('size').value = '8';
  document.getElementById('precision').value = 'int8';
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
function boardReport(overrides = {}) {
  return {id: 'board-child', evidence: 'board_measured', physical_fpga: true, correct: true, parent_run_id: 'fixture-run', recorded_at: '2026-11-14T01:02:03Z', build: {bitstream_sha256: 'b'.repeat(64), target_part: 'xck26-sfvc784-2LV-c', parameters: {N: 8, LANES: 4}, configured_clock_hz: 100000000}, board: {sku: 'SK-KV260-G', board_revision: 'Rev A', image_identity: 'ubuntu-fixture'}, run: {cycles: 128, outputs: Array(64).fill(0), host_elapsed_ns: null, programming_elapsed_ns: null}, ...overrides};
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
    else if (url === '/api/explore') data = {spec: body.spec, candidates: [1, 2, 4].map(lanes => ({lanes, id: 'mac' + lanes, within_lane_limit: lanes <= body.spec.max_lanes, cycles: 512 / lanes, projected_us: 5.12 / lanes})), provisional: 'mac4', warning: 'Unverified resources.'};
    else throw new Error('Unconfigured fixture URL: ' + url);
    return {ok, json: async () => data};
  };
  const context = vm.createContext({document, fetch, Blob, URL, setTimeout, matchMedia: () => ({matches: true})});
  vm.runInContext(script + '\n;globalThis.ui={state,readSpec,fillSpec,updateTarget,updateGenerateRtl,setBusy,comparable,comparison,renderResult,renderBoardResult,importBoardResult,renderSynthesis,history,generateRtl,updatePipeline,explore};', context);
  await new Promise(resolve => setImmediate(resolve));
  const get = id => document.getElementById(id);
  return {ui: context.ui, get, document, routes, calls, reports, prompt(value) {get('prompt').value = value; get('prompt').oninput();}};
}

test('physical board and Vivado importers appear only for FPGA target', async () => {
  const a = await app();
  assert.equal(a.get('board-evidence').hidden, false);
  assert.equal(a.get('vivado-import').hidden, false);
  a.ui.state.spec.target = 'asic'; a.ui.updateTarget();
  assert.equal(a.get('board-evidence').hidden, true);
  assert.equal(a.get('vivado-import').hidden, true);
  a.ui.state.spec.target = 'kv260'; a.ui.updateTarget();
  assert.equal(a.get('board-evidence').hidden, false);
  assert.equal(a.get('vivado-import').hidden, false);
});

test('catalog assembly requires local verification tools, not AI or a prompt', async () => {
  const a = await app();
  assert.equal(a.get('generate-rtl').disabled, false);
  a.prompt('   '); assert.equal(a.get('generate-rtl').disabled, false);
  a.ui.state.ai = false; a.ui.updateGenerateRtl();
  assert.equal(a.get('generate-rtl').disabled, false, 'Groq only explains the reviewed architecture');
  a.ui.state.simulator = false; a.ui.updateGenerateRtl();
  assert.equal(a.get('generate-rtl').disabled, true);
  a.ui.state.simulator = true;
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
  assert.match(a.get('generate-rtl-help').textContent, /qualified 1-lane catalog recipe/);
});

test('one click sends the reviewed spec and selected catalog lanes, then renders checked-in evidence', async () => {
  const a = await app(), result = rtlReport({evidence: 'rtl_simulation', prompt: undefined});
  a.routes.set('/api/build', async body => {
    assert.deepEqual(body, {spec, lanes: 4});
    assert.equal(a.get('generate-rtl').disabled, true);
    a.reports.push(result); return {data: result};
  });
  await a.get('generate-rtl').onclick();
  assert.equal(a.ui.state.result.id, result.id);
  assert.match(a.get('result').innerHTML, /CHECKED-IN RTL SIMULATION/);
  assert.match(a.get('history').innerHTML, /Checked-in RTL simulation/);
  assert.equal(a.get('stale-result').hidden, true);
  assert.equal(a.get('generate-rtl').disabled, false);
  assert.equal(a.ui.state.busy, false);
  assert.equal(a.get('export').disabled, false);
});

test('ASIC catalog build labels synthesis separately and becomes stale only on configuration edits', async () => {
  const synthesis = asicReport({source_origin: 'checked_in_rtl'});
  const a = await app(), result = rtlReport({evidence: 'rtl_simulation', prompt: undefined, spec: {...spec, target: 'asic'}, synthesis, synthesis_verified: true});
  a.ui.fillSpec(result.spec);
  a.routes.set('/api/build', async () => ({data: result}));
  await a.get('generate-rtl').onclick();
  assert.equal(a.ui.state.synthesis, result.synthesis);
  assert.match(a.get('synthesis-result').innerHTML, /GENERIC SYNTHESIS · NOT A PHYSICAL CHIP/);
  assert.doesNotMatch(a.get('synthesis-result').innerHTML, /Source: AI-generated RTL/);
  assert.match(a.get('synthesis-result').innerHTML, /not standard-cell area/);
  assert.equal(a.get('stale-result').hidden, true);
  assert.equal(a.get('stale-synthesis').hidden, true);
  assert.equal(a.get('export-netlist').disabled, false);
  a.prompt('This optional prompt should not change catalog evidence');
  assert.equal(a.get('stale-result').hidden, true);
  assert.equal(a.get('stale-synthesis').hidden, true);
  a.get('size').value = '16'; a.get('size').oninput();
  assert.equal(a.get('stale-result').hidden, false);
  assert.equal(a.get('stale-synthesis').hidden, false);
});

test('generic synthesis shows design-sensitive register and other logic counts', async () => {
  const a = await app();
  a.ui.renderSynthesis(asicReport({cell_count: 10, cell_counts: {'$_DFFE_PP_': 3, '$_SDFF_PP0_': 1, '$_MUX_': 4, '$_AND_': 2}}));
  const result = a.get('synthesis-result').innerHTML;
  assert.match(result, /REGISTER CELLS<\/small><strong>4<\/strong>/);
  assert.match(result, /OTHER LOGIC CELLS<\/small><strong>6<\/strong>/);
  assert.match(result, /They are not standard-cell area or power/);
});

test('ASIC architecture cards show known MAC lanes instead of unknown area', async () => {
  const a = await app();
  a.ui.fillSpec({...spec, target: 'asic'});
  await a.ui.explore();
  const cards = a.get('candidate-grid').innerHTML;
  assert.match(cards, /MAC LANES<\/small><strong>1<\/strong>/);
  assert.match(cards, /MAC LANES<\/small><strong>4<\/strong>/);
  assert.doesNotMatch(cards, /PHYSICAL AREA/);
});

test('supported presets update real configuration controls and exploration', async () => {
  const a = await app();
  await a.document.querySelector('[data-preset="16-4"]').click();
  assert.equal(a.get('size').value, 16);
  assert.equal(a.get('max_lanes').value, 4);
  assert.equal(a.get('objective').value, 'minimize_latency');
  assert.equal(a.calls.at(-1).body.spec.size, 16);
  assert.match(a.get('candidate-grid').innerHTML, /MAC/);
  await a.document.querySelector('[data-preset="8-1"]').click();
  assert.equal(a.get('size').value, 8);
  assert.equal(a.get('max_lanes').value, 1);
  assert.equal(a.get('objective').value, 'minimize_lanes');
  assert.equal(a.calls.at(-1).body.spec.max_lanes, 1);
  await a.document.querySelector('[data-preset="16-2"]').click();
  assert.equal(a.get('size').value, 16);
  assert.equal(a.get('max_lanes').value, 2);
  assert.match(a.get('candidate-grid').innerHTML, /2 arithmetic lanes process 2 output columns/);
});

test('two-lane comparison uses two verified simulations', async () => {
  const reports = [], a = await app({runs: reports});
  a.ui.fillSpec({...spec, max_lanes: 2});
  await a.ui.explore();
  const used = [];
  a.routes.set('/api/simulate', async body => {
    used.push(body.lanes);
    const report = rtlReport({id: `sim-${body.lanes}`, spec: body.spec, evidence: 'rtl_simulation', prompt: undefined, lanes: body.lanes, cycles: 512 / body.lanes, projected_us: 5.12 / body.lanes});
    reports.push(report);
    return {data: report};
  });
  await a.get('compare').onclick();
  assert.deepEqual(used, [1, 2]);
  assert.match(a.get('result').innerHTML, /1 lane: 512 cycles → 2 lanes: 256 cycles/);
});

test('rejection preserves prior verified evidence and reports an honest visible error', async () => {
  const a = await app(), prior = rtlReport({id: 'prior-verified'});
  a.prompt(prior.prompt); a.ui.renderResult(prior);
  const previous = a.get('result').innerHTML;
  a.routes.set('/api/build', async () => ({ok: false, data: {error: 'Catalog RTL simulation failed; no result accepted.'}}));
  await a.get('generate-rtl').onclick();
  assert.equal(a.get('result').innerHTML, previous);
  assert.equal(a.ui.state.result.id, 'prior-verified');
  assert.match(a.get('notice').textContent, /simulation failed/);
  assert.match(a.get('notice').textContent, /previously verified report remains displayed/);
  assert.equal(a.get('notice').className, 'notice error');
  assert.equal(a.get('generate-rtl').disabled, false);
});

test('unverified or incomplete successful responses never replace accepted evidence', async () => {
  for (const result of [rtlReport({evidence: 'rtl_simulation', prompt: undefined, correct: false}), rtlReport({evidence: 'ai_generated_rtl'}), rtlReport({evidence: 'rtl_simulation', prompt: undefined, spec: {...spec, target: 'asic'}})]) {
    const a = await app(); a.ui.fillSpec(result.spec); a.prompt(result.prompt);
    a.routes.set('/api/build', async () => ({data: result}));
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
  assert.doesNotMatch(a.ui.comparison(generated), /fewer simulated compute cycles/);
  a.ui.state.runs = [other];
  assert.match(a.ui.comparison(generated), /MATCHED AI RTL SIMULATION CAPACITY COMPARISON/);
  assert.match(a.ui.comparison(generated), /more arithmetic capacity/);
  assert.match(a.ui.comparison(generated), /not a physical speedup measurement/);
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
  const verifyStage = a.document.querySelectorAll('[data-stage]').find(stage => stage.dataset.stage === 'verify');
  assert.doesNotMatch(verifyStage.className, /passed/);
});

test('example prompt buttons enable generation and mark generated evidence stale', async () => {
  const a = await app(), result = rtlReport(); a.prompt(result.prompt); a.ui.renderResult(result);
  a.document.querySelectorAll('[data-example]')[0].onclick();
  assert.equal(a.get('generate-rtl').disabled, false);
  assert.equal(a.get('stale-result').hidden, false);
});

test('architecture map renders reviewed parameters while Groq supplies explanation only', async () => {
  const a = await app();
  assert.equal(a.get('architecture-map-container').hidden, true);
  a.routes.set('/api/plan', async body => {
    assert.deepEqual(body, {spec});
    return {data: {evidence: 'build_plan', spec, block_id: 'siliconos.matmul.parallel4.v1', parameters: {N: 8, LANES: 4}}};
  });
  await a.get('develop-block-diagram').onclick();
  assert.equal(a.get('architecture-map-container').hidden, false);
  assert.match(a.get('architecture-map-container').innerHTML, /siliconos\.matmul\.parallel4\.v1/);
  assert.match(a.get('architecture-map-container').innerHTML, /CONCEPTUAL · NOT VIVADO/);
  assert.match(a.get('architecture-map-container').innerHTML, /MAC 4/);
  assert.match(a.get('architecture-map-container').innerHTML, /RTL DATA PATH/);
  assert.match(a.get('architecture-map-container').innerHTML, /32-bit acc/);
  assert.match(a.get('architecture-map-container').innerHTML, /not a BRAM mapping claim/);
  a.routes.set('/api/architecture-map', async body => {
    assert.deepEqual(body, {spec});
    return {data: {title: 'A clear compute path', summary: 'Four lanes use more arithmetic capacity.', selection_reason: 'The reviewed objective favors lower modeled cycles.', assumptions: ['Clock is requested, not measured.']}};
  });
  await a.document.querySelector('[data-architecture-map]').onclick();
  assert.match(a.get('architecture-map-container').innerHTML, /A clear compute path/);
  assert.match(a.get('architecture-map-container').innerHTML, /graph remain deterministic/);
});


test('history refresh failure preserves successful generation without falsely reporting rejection', async () => {
  const a = await app(), result = rtlReport({evidence: 'rtl_simulation', prompt: undefined});
  a.routes.set('/api/build', async () => ({data: result}));
  a.routes.set('/api/runs', async () => ({ok: false, data: {error: 'History temporarily unavailable'}}));
  await a.get('generate-rtl').onclick();
  assert.equal(a.ui.state.result, result);
  assert.match(a.get('notice').textContent, /Catalog verification passed/);
  assert.match(a.get('notice').textContent, /history could not be refreshed/);
  assert.doesNotMatch(a.get('notice').textContent, /assembly rejected|previously verified/);
  assert.equal(a.get('export').disabled, false);
});

test('direct controls lead the existing six-stage evidence pipeline', async () => {
  assert.ok(html.indexOf('id="spec-form"') < html.indexOf('id="prompt-panel"'), 'direct controls should precede optional prompting');
  for (const label of ['Configure', 'Select RTL', 'Verify', 'Implement', 'Run on KV260', 'Export']) assert.match(html, new RegExp(label));
  assert.match(html, /Optional drafting assist/);
  const a = await app();
  const stages = Object.fromEntries(a.document.querySelectorAll('[data-stage]').map(stage => [stage.dataset.stage, stage]));
  assert.match(stages.configure.className, /passed/);
  assert.match(stages.select.className, /selected/);
  assert.match(stages.verify.className, /waiting/);
  assert.match(stages.implement.className, /waiting/);
  assert.match(stages.board.className, /waiting/);
  assert.match(a.get('candidate-grid').innerHTML, /PROJECTED KERNEL TIME · NOT MEASURED/);
  assert.match(a.get('candidate-grid').innerHTML, /MHz assumed/);
});

test('verified simulation enables selected-run handoff and truthful pipeline states', async () => {
  const a = await app(), result = rtlReport({evidence: 'rtl_simulation', prompt: undefined});
  a.ui.renderResult(result);
  assert.equal(a.get('handoff').disabled, false);
  assert.equal(a.get('export').disabled, false);
  assert.equal(a.get('board-result-file').disabled, false);
  assert.match(a.get('result').innerHTML, /ASSUMED TARGET CLOCK · NOT MEASURED/);
  a.get('handoff').onclick();
  const anchor = a.document.created.at(-1);
  assert.equal(anchor.href, '/api/runs/fixture-run/handoff.zip');
  assert.equal(anchor.download, 'siliconos-fixture-run-handoff.zip');
  assert.equal(anchor.clicked, true);
  const stages = Object.fromEntries(a.document.querySelectorAll('[data-stage]').map(stage => [stage.dataset.stage, stage]));
  assert.match(stages.select.className, /passed/);
  assert.match(stages.verify.className, /passed/);
  assert.match(stages.export.className, /selected/);
  assert.doesNotMatch(stages.implement.className, /passed/);
});

test('run-both comparison describes a capacity trade rather than physical speedup', async () => {
  const reports = [], a = await app({runs: reports});
  let call = 0;
  a.routes.set('/api/simulate', async body => {
    call++;
    const report = rtlReport({id: `sim-${body.lanes}`, evidence: 'rtl_simulation', prompt: undefined, lanes: body.lanes, cycles: body.lanes === 1 ? 512 : 128, projected_us: body.lanes === 1 ? 5.12 : 1.28});
    reports.push(report);
    return {data: report};
  });
  await a.get('compare').onclick();
  assert.equal(call, 2);
  assert.match(a.get('result').innerHTML, /4\.00× fewer simulated compute cycles/);
  assert.match(a.get('result').innerHTML, /more arithmetic capacity/i);
  assert.match(a.get('result').innerHTML, /not a physical speedup measurement/i);
  assert.doesNotMatch(a.get('result').innerHTML, /optimized|measured hardware speedup/i);
});

test('board-result JSON posts to the selected parent and renders separate recorded evidence', async () => {
  const a = await app(), parent = rtlReport({evidence: 'rtl_simulation', prompt: undefined}), payload = {schema_version: 1, parent_run_id: parent.id, evidence: 'board_measured'}, board = boardReport();
  a.ui.renderResult(parent);
  a.get('board-result-file').files = [{text: async () => JSON.stringify(payload)}];
  a.get('board-result-file').onchange();
  assert.equal(a.get('import-board-result').disabled, false);
  a.routes.set('/api/runs/fixture-run/board-result', async body => {
    assert.deepEqual(body, payload);
    return {data: board};
  });
  await a.get('import-board-result').onclick();
  assert.equal(a.ui.state.result, parent, 'physical evidence must not replace the selected simulation');
  assert.equal(a.ui.state.boardResult, board);
  assert.match(a.get('board-result').innerHTML, /RECORDED BOARD MEASUREMENT · PARENT RUN VERIFIED/);
  assert.match(a.get('board-result').innerHTML, /fixture-run/);
  assert.match(a.get('board-result').innerHTML, new RegExp('b{64}'));
  assert.match(a.get('board-result').innerHTML, /xck26-sfvc784-2LV-c · N=8 · LANES=4/);
  assert.match(a.get('board-result').innerHTML, /SK-KV260-G · Rev A/);
  assert.match(a.get('board-result').innerHTML, /ubuntu-fixture/);
  assert.match(a.get('board-result').innerHTML, /100 MHz/);
  assert.match(a.get('board-result').innerHTML, /128/);
  assert.match(a.get('board-result').innerHTML, /All 64 outputs matched the server oracle/);
  assert.match(a.get('board-result').innerHTML, /2026-11-14T01:02:03Z/);
  const boardStage = a.document.querySelectorAll('[data-stage]').find(stage => stage.dataset.stage === 'board');
  assert.match(boardStage.className, /passed/);
});

test('runner availability and recorded evidence remain distinct', async () => {
  const a = await app({status: {board: true}}), parent = rtlReport({evidence: 'rtl_simulation', prompt: undefined});
  const boardStage = a.document.querySelectorAll('[data-stage]').find(stage => stage.dataset.stage === 'board');
  assert.match(boardStage.className, /selected/);
  assert.doesNotMatch(boardStage.className, /passed/);
  assert.match(a.get('target-state').textContent, /Board runner available/);
  a.ui.renderResult(parent);
  a.ui.renderBoardResult(boardReport());
  assert.match(a.get('board-result').innerHTML, /RECORDED BOARD MEASUREMENT · PARENT RUN VERIFIED/);
  assert.match(a.get('target-state').textContent, /Recorded KV260 runs available/);
});

test('recorded results do not produce a false disconnected warning', async () => {
  const a = await app({status: {board: false, board_recorded: true}});
  assert.match(a.get('target-state').textContent, /Recorded KV260 runs available/);
  assert.match(a.get('board-connection-label').textContent, /RECORDED BOARD RUNS/);
  assert.doesNotMatch(a.get('target-state').textContent, /not connected/i);
});

test('ASIC stage separates app generic synthesis from recorded SKY130 physical research', () => {
  assert.match(html, /Separate SKY130 research/);
  assert.match(html, /recorded technology mapping and routed physical-design artifacts/);
  assert.match(html, /slew, capacitance, fanout, and antenna violations remain/);
  assert.match(html, /separate from the app’s generic synthesis and is not signoff clean/);
});
