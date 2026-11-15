/* Visual status for long tool requests. The server does not stream stage progress. */
(() => {
  const operations = {
    '/api/generate-rtl': {title: 'Generate & verify RTL', stages: ['Groq RTL draft', 'Source gate and RTL simulation', 'Integer-oracle verification']},
    '/api/asic/synthesize': {title: 'Synthesize generic logic', stages: ['Yosys synthesis', 'Netlist simulation', 'Integer-oracle verification']},
    '/api/build': {title: 'Build verified design', stages: ['RTL simulation', 'Integer-oracle verification']},
  };
  const panel = document.createElement('section');
  panel.className = 'tool-progress';
  panel.hidden = true;
  panel.setAttribute('aria-label', 'Build activity');
  panel.innerHTML = '<div class="tool-progress-head"><div><span class="tool-progress-kicker">LIVE TOOL RUN</span><h3 id="tool-progress-title"></h3></div><button id="tool-progress-hide" type="button" aria-label="Hide build activity">×</button></div><p id="tool-progress-status" role="status" aria-live="polite"></p><div class="tool-progress-track" aria-hidden="true"><span></span></div><ol id="tool-progress-stages"></ol><p class="tool-progress-foot"><span id="tool-progress-elapsed" aria-hidden="true">0s elapsed</span><span>Stage timing is not reported by the server.</span></p>';
  document.body.appendChild(panel);
  const title = panel.querySelector('#tool-progress-title');
  const status = panel.querySelector('#tool-progress-status');
  const stages = panel.querySelector('#tool-progress-stages');
  const elapsed = panel.querySelector('#tool-progress-elapsed');
  const track = panel.querySelector('.tool-progress-track');
  panel.querySelector('#tool-progress-hide').onclick = () => { panel.hidden = true; };
  let timer = null;
  let started = 0;

  function begin(path, spec) {
    const operation = operations[path];
    const steps = [...operation.stages];
    if (spec?.target === 'asic' && path !== '/api/asic/synthesize') steps.push('Yosys and netlist verification');
    title.textContent = operation.title;
    status.textContent = 'Server request running. The listed checks are expected; their individual progress is not reported.';
    stages.replaceChildren(...steps.map(label => {
      const item = document.createElement('li');
      item.textContent = label;
      item.className = 'pending';
      return item;
    }));
    panel.hidden = false;
    panel.classList.remove('complete', 'failed');
    panel.setAttribute('aria-busy', 'true');
    track.hidden = false;
    started = Date.now();
    elapsed.textContent = '0s elapsed';
    clearInterval(timer);
    timer = setInterval(() => { elapsed.textContent = `${Math.floor((Date.now() - started) / 1000)}s elapsed`; }, 1000);
  }

  function finish(path, report, ok) {
    clearInterval(timer);
    timer = null;
    elapsed.textContent = `${Math.floor((Date.now() - started) / 1000)}s elapsed`;
    panel.setAttribute('aria-busy', 'false');
    track.hidden = true;
    const simulation = report?.correct === true && ['rtl_simulation', 'ai_generated_rtl'].includes(report?.evidence);
    const synthesis = report?.correct === true && report?.evidence === 'generic_synthesis';
    const nestedSynthesis = report?.synthesis_verified === true && report?.synthesis?.correct === true && report?.synthesis?.evidence === 'generic_synthesis';
    const asic = report?.spec?.target === 'asic';
    const accepted = ok && (path === '/api/asic/synthesize' ? synthesis : simulation && (!asic || nestedSynthesis));
    panel.classList.toggle('complete', accepted);
    panel.classList.toggle('failed', !accepted);
    for (const item of stages.children) item.className = accepted ? 'passed' : 'unconfirmed';
    status.textContent = accepted
      ? 'The server returned verified evidence. Inspect the report and source hashes below.'
      : 'The run did not return accepted verified evidence. Review the error shown in the workbench.';
  }

  const originalFetch = window.fetch.bind(window);
  window.fetch = async (input, options) => {
    const path = typeof input === 'string' ? input.split('?')[0] : input?.url?.split('?')[0];
    if (!(path in operations) || options?.method !== 'POST') return originalFetch(input, options);
    let spec;
    try { spec = JSON.parse(options.body)?.spec; } catch (_) { /* The backend validates malformed input. */ }
    begin(path, spec);
    try {
      const response = await originalFetch(input, options);
      const originalJson = response.json.bind(response);
      response.json = async () => {
        try {
          const report = await originalJson();
          finish(path, report, response.ok);
          return report;
        } catch (error) {
          finish(path, null, false);
          throw error;
        }
      };
      return response;
    } catch (error) {
      finish(path, null, false);
      throw error;
    }
  };
})();
