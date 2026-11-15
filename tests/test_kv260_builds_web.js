const test = require('node:test');
const assert = require('node:assert/strict');
const {renderComparison, loadComparison} = require('../web/kv260-builds.js');
const fixture = () => ({evidence:'routed_implementation_comparison',scope:'whole design',builds:[1,4].map(lanes=>({id:`n8_l${lanes}`,parameters:{N:8,LANES:lanes},stage:'Routed',vivado_version:'2025.2',part:'xck26',resources:{lut:lanes*1000,ff:lanes*500,dsp:0},timing:{wns_ns:0.125,tns_ns:0,whs_ns:0.04,ths_ns:0,wpws_ns:4.5,tpws_ns:0,constraints_met:true},source_sha256:{'matmul.sv':'abc'},manifest_sha256:'manifest',report_sha256:{'utilization.rpt':'util-hash','timing_summary.rpt':'timing-hash'},reports:{'utilization.rpt':'DSPs | 0 <script>alert(1)</script>','timing_summary.rpt':'Design Timing Summary'}}))});
test('comparison labels whole-design routed evidence and links counts including zero to original reports',()=>{
  const html = renderComparison(fixture());
  assert.match(html,/Whole-design LUTs/);assert.match(html,/Whole-design flip-flops/);assert.match(html,/Whole-design DSPs/);
  assert.match(html,/Routed/);assert.match(html,/2025\.2/);assert.match(html,/0\.125 ns/);
  assert.match(html,/href="#kv260-report-0-utilization"[^>]*>0</);assert.match(html,/id="kv260-report-1-timing"/);
  assert.match(html,/util-hash/);assert.match(html,/&lt;script&gt;/);assert.doesNotMatch(html,/<script>/);
  assert.match(html,/do not prove physical board execution/);assert.doesNotMatch(html,/512 cycles|128 cycles|board-result\.json/);
  assert.match(html,/Whole-design resources/);assert.match(html,/Routed setup margin/);
  assert.match(html,/class="kv260-chart-fill kv260-chart-fill-0" style="width:25\.00%"/);
  assert.match(html,/class="kv260-chart-fill kv260-chart-fill-1" style="width:100\.00%"/);
  assert.match(html,/href="#kv260-report-1-utilization"[^>]*>4,000/);
});
test('rejects other evidence scopes before rendering values',()=>{
  const data=fixture();data.scope='kernel';assert.throws(()=>renderComparison(data),/whole-design/);
  data.scope='whole design';data.evidence='board_measured';assert.throws(()=>renderComparison(data),/whole-design/);
});
test('failed hash verification clears previous comparison and displays server error',async()=>{
  const output={innerHTML:'old counts'},status={},button={disabled:false};
  await loadComparison(async()=>({ok:false,json:async()=>({error:'Report hash mismatch'})}),output,status,button);
  assert.equal(output.innerHTML,'');assert.match(status.textContent,/Report hash mismatch/);assert.equal(button.disabled,false);
});
test('successful request renders both verified builds and releases loading state',async()=>{
  const output={},status={},button={disabled:false};
  await loadComparison(async url=>{assert.equal(url,'/api/kv260/builds');assert.equal(button.disabled,true);return {ok:true,json:async()=>fixture()};},output,status,button);
  assert.match(output.innerHTML,/4 lanes/);assert.match(status.textContent,/Both builds verified/);assert.equal(button.disabled,false);
});
test('archived comparison discloses a changed active RTL checkout',async()=>{
  const data=fixture();data.current_rtl_matches_build=false;
  const output={},status={},button={disabled:false};
  await loadComparison(async()=>({ok:true,json:async()=>data}),output,status,button);
  assert.match(output.innerHTML,/active RTL has changed/);
  assert.match(status.textContent,/archived RTL/);
  assert.match(output.innerHTML,/Whole-design LUTs/);
});
