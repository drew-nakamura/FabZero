/* Routed implementation evidence stays independent from simulation and board runs. */
(function () {
  'use strict';
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function renderComparison(data) {
    if (data.evidence !== 'routed_implementation_comparison' || data.scope !== 'whole design' || !Array.isArray(data.builds) || data.builds.length !== 2) throw new Error('A verified whole-design comparison is unavailable.');
    const builds = data.builds;
    const reportId = (i, type) => `kv260-report-${i}-${type}`;
    const metric = (value, i, type, unit = '') => value === null || value === undefined ? '<span>Not reported</span>' : `<a href="#${reportId(i, type)}" data-build-report="${reportId(i, type)}">${esc(value)}${unit}<span aria-hidden="true"> ↗</span></a>`;
    const row = (label, values) => `<tr><th scope="row">${label}</th>${values.map(v => `<td>${v}</td>`).join('')}</tr>`;
    const resources = [['Whole-design LUTs','lut'],['Whole-design flip-flops','ff'],['Whole-design DSPs','dsp']].map(([label,key]) => row(label,builds.map((b,i)=>metric(b.resources[key],i,'utilization')))).join('');
    const timing = [['Setup slack · WNS','wns_ns'],['Total setup slack · TNS','tns_ns'],['Hold slack · WHS','whs_ns'],['Total hold slack · THS','ths_ns'],['Pulse-width slack · WPWS','wpws_ns'],['Total pulse-width slack · TPWS','tpws_ns']].map(([label,key])=>row(label,builds.map((b,i)=>metric(b.timing[key],i,'timing',' ns')))).join('');
    const reports = builds.map((b,i)=>`<article class="kv260-build-sources"><h3>8×8 · ${esc(b.parameters.LANES)} lane${b.parameters.LANES===1?'':'s'} — source reports</h3>${[['utilization','utilization.rpt'],['timing','timing_summary.rpt']].map(([type,file])=>`<details id="${reportId(i,type)}"><summary>${esc(file)} <span>Inspect report</span></summary><p>SHA-256 <code>${esc(b.report_sha256[file])}</code></p><pre tabindex="0">${esc(b.reports[file])}</pre></details>`).join('')}<details><summary>Verified manifest and RTL hashes</summary><p>Manifest <code>${esc(b.manifest_sha256)}</code></p>${Object.entries(b.source_sha256).map(([file,hash])=>`<p>${esc(file)} <code>${esc(hash)}</code></p>`).join('')}</details></article>`).join('');
    const sourceNote = data.current_rtl_matches_build === false ? '<p>The active RTL has changed since these archived builds. These values apply to the verified archived source hashes shown below.</p>' : '';
    const resourceValues = builds.flatMap(b=>[b.resources.lut,b.resources.ff,b.resources.dsp]);
    const resourceScale = Math.max(1000, Math.ceil(Math.max(...resourceValues)/1000)*1000);
    const wnsScale = Math.max(1, Math.ceil(Math.max(...builds.map(b=>b.timing.wns_ns))));
    const bar = (value, i, maximum, type, unit='') => {
      if (typeof value !== 'number' || !Number.isFinite(value)) return '<span class="kv260-chart-missing">Not reported</span>';
      const width = Math.max(0, Math.min(100, value/maximum*100));
      return `<div class="kv260-chart-bar-row"><span class="kv260-chart-lane">${esc(builds[i].parameters.LANES)}L</span><span class="kv260-chart-track"><span class="kv260-chart-fill kv260-chart-fill-${i}" style="width:${width.toFixed(2)}%"></span></span>${metric(value.toLocaleString('en-US'),i,type,unit)}</div>`;
    };
    const chartRow = (label, values, maximum, type, unit='') => `<div class="kv260-chart-group"><div class="kv260-chart-group-title">${esc(label)}</div>${values.map((value,i)=>bar(value,i,maximum,type,unit)).join('')}</div>`;
    const resourcePlot = chartRow('LUTs',builds.map(b=>b.resources.lut),resourceScale,'utilization')+chartRow('Flip-flops',builds.map(b=>b.resources.ff),resourceScale,'utilization')+chartRow('DSPs',builds.map(b=>b.resources.dsp),resourceScale,'utilization');
    const timingPlot = chartRow('Setup slack · WNS',builds.map(b=>b.timing.wns_ns),wnsScale,'timing',' ns');
    const visual = `<div class="kv260-visual-head"><div><span class="eyebrow">ROUTED IMPLEMENTATION / VIVADO ${esc(builds[0].vivado_version)}</span><h3>What four lanes cost in fabric.</h3></div><div class="kv260-visual-legend"><span><i class="kv260-legend-one"></i> 1 lane</span><span><i class="kv260-legend-four"></i> 4 lanes</span></div></div><div class="kv260-visual-grid"><figure class="kv260-chart-card"><figcaption><strong>Whole-design resources</strong><span>Shared scale · 0 to ${esc(resourceScale.toLocaleString('en-US'))}</span></figcaption>${resourcePlot}<div class="kv260-chart-axis"><span>0</span><span>${esc(resourceScale.toLocaleString('en-US'))}</span></div></figure><figure class="kv260-chart-card kv260-chart-card-timing"><figcaption><strong>Routed setup margin</strong><span>Shared scale · 0 to ${esc(wnsScale)} ns</span></figcaption>${timingPlot}<div class="kv260-chart-axis"><span>0 ns</span><span>${esc(wnsScale)} ns</span></div><p>Positive slack means this build met its setup constraint. It is not kernel latency.</p></figure></div>`;
    return `<div class="kv260-comparison-banner"><span class="tag">HASHES VERIFIED</span><p>Whole-design implementation reports include board integration logic. Simulated kernel cycles remain in the simulation results; these reports do not prove physical board execution.</p>${sourceNote}</div>${visual}<div class="kv260-table-scroll"><table class="kv260-build-table"><caption>Exact routed values · signed INT8 · 8×8</caption><thead><tr><th scope="col">Implementation evidence</th>${builds.map(b=>`<th scope="col">${esc(b.parameters.LANES)} lane${b.parameters.LANES===1?'':'s'}</th>`).join('')}</tr></thead><tbody>${row('Report stage',builds.map(b=>esc(b.stage)))}${row('Vivado version',builds.map(b=>esc(b.vivado_version)))}${row('Device',builds.map(b=>esc(b.part)))}${resources}${timing}${row('Report timing constraints',builds.map((b,i)=>metric(b.timing.constraints_met===true?'Met':b.timing.constraints_met===false?'Not met':null,i,'timing')))}</tbody></table></div><p class="kv260-inspect-hint">Select a value to open its original report. Slack is reported timing margin, not a measured board latency.</p><div class="kv260-sources">${reports}</div>`;
  }
  async function loadComparison(fetcher, output, status, button) {
    output.innerHTML = ''; button.disabled = true; status.textContent = 'Checking report and RTL hashes…';
    try {
      const response = await fetcher('/api/kv260/builds');
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Build comparison unavailable.');
      output.innerHTML = renderComparison(data);
      status.textContent = data.current_rtl_matches_build === false ? 'Both builds verified against their archived RTL; active RTL has since changed.' : 'Both builds verified against their manifests and RTL.';
    } catch (error) {output.innerHTML = ''; status.textContent = `Comparison unavailable: ${error.message}`;}
    finally {button.disabled = false;}
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {renderComparison, loadComparison};
  if (typeof document === 'undefined') return;
  const panel = document.getElementById('kv260-builds');
  if (!panel) return;
  const button = document.getElementById('compare-kv260-builds');
  const output = document.getElementById('kv260-builds-result');
  button.addEventListener('click', () => loadComparison(fetch, output, document.getElementById('kv260-builds-status'), button));
  output.addEventListener('click', event => {
    const link = event.target.closest('[data-build-report]');
    if (link) document.getElementById(link.dataset.buildReport).open = true;
  });
  const existing = document.getElementById('vivado-import');
  const syncTarget = () => {panel.hidden = existing.hidden;};
  syncTarget();
  new MutationObserver(syncTarget).observe(existing, {attributes:true,attributeFilter:['hidden']});
})();
