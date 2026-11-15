// Demo flow: prompt -> AI spec & architecture -> block diagram -> RTL -> Vivado -> KV260 -> results.
// Each step appears as it runs and shows its real artifacts. Uses globals from app.js
// (state, api, escapeHtml, notice, readSpec, fillSpec, explore, setBusy, history, sameObject, bindRunLinks,
// renderBoardState, paintBoard, KV260_SVG).
const FLOW=[['prompt','Prompt'],['spec','Spec & architecture'],['diagram','Block diagram'],['rtl','RTL'],['vivado','Vivado'],['board','KV260'],['results','Results']];
const STEP_DWELL_MS=1000; // demo pacing: a finished RTL/Vivado step stays on screen this long before the next one appears
const SERIES={1:'#2a78d6',4:'#eb6834'}; // validated categorical pair (dataviz validator: all checks pass on the card surface)
const pipe={mode:null,running:false,status:{},error:{},spec:null,origin:null,sims:{},handoffs:{},builds:null,check:null,jobs:{},boards:{},excerpts:{},transcripts:{},startedAt:null,elapsed:null,note:null,specShown:false,revealed:new Set()};
const pfmt=v=>v===null||v===undefined||Number.isNaN(v)?'—':Number(v).toLocaleString();
const pshort=h=>h?escapeHtml(String(h).slice(0,12))+'…':'—';
const psleep=ms=>new Promise(r=>setTimeout(r,ms));
const pLanes=()=>Object.keys(pipe.sims).map(Number).sort((a,b)=>a-b);
const laneName=l=>`${l} lane${l>1?'s':''}`;
const swatch=l=>`<i class="swatch" style="background:${SERIES[l]||'#7d8b75'}"></i>`;
function stepError(step,message){const e=new Error(message);e.step=step;return e;}
function resetPipe(mode){Object.assign(pipe,{mode,running:false,status:{},error:{},spec:null,origin:null,sims:{},handoffs:{},check:null,jobs:{},boards:{},excerpts:{},transcripts:{},startedAt:null,elapsed:null,note:null,revealed:new Set()});}
async function fetchText(path){const r=await fetch(path);if(!r.ok)throw new Error('Could not load '+path);return r.text();}
function kv(label,value,cls=''){return `<div class="kv ${cls}"><small>${label}</small><strong>${value}</strong></div>`;}
function laneGrid(cards){return `<div class="lane-cards">${cards.join('')}</div>`;}
function chip(status){return {waiting:'',ready:'<span class="step-chip ready">● Ready</span>',running:'<span class="step-chip running">◌ Running…</span>',done:'<span class="step-chip done">✓ Done</span>',failed:'<span class="step-chip failed">✗ Failed</span>',skipped:'<span class="step-chip">— Skipped</span>'}[status]||'';}
function merge(...xs){xs=xs.map(x=>x||'waiting');if(xs.includes('failed'))return 'failed';if(xs.every(x=>x==='skipped'))return 'skipped';if(xs.every(x=>x==='done'||x==='skipped'))return 'done';if(xs.some(x=>x==='running'||x==='done'))return 'running';return 'waiting';}
function flowStatus(key){const s=pipe.status,shown=pipe.specShown||pipe.mode;return {prompt:pipe.specShown?'done':'ready',spec:s.sim?'done':pipe.specShown?'ready':'waiting',diagram:shown?(diag.status==='waiting'?'running':diag.status):'waiting',rtl:merge(s.sim,s.handoff),vivado:s.vivado||'waiting',board:merge(s.board,s.run,s.import),results:s.compare||'waiting'}[key];}
function flowError(key){const e=pipe.error;return {diagram:diag.error,rtl:e.sim||e.handoff,vivado:e.vivado,board:e.board||e.run||e.import,results:e.compare}[key];}

// ---------------------------------------------------------------- 02 spec & architecture
function specOriginText(){const o=state.specOrigin||{};if(o.kind==='ai')return `Drafted by AI${o.model?' ('+escapeHtml(o.model)+')':''} from your prompt${o.edited?', then edited by hand':''}. Review it, then build.`;if(o.kind==='example')return `Built-in example${o.edited?', then edited by hand':''}. Review it, then build.`;if(o.kind==='recorded')return 'From the recorded run.';return 'Review the specification, then build. Both architectures run on the same inputs.';}
function specNotes(){const o=state.specOrigin||{};if(o.kind!=='ai')return '';return `${o.prompt?`<blockquote class="prompt-quote">“${escapeHtml(o.prompt)}”</blockquote>`:''}${o.explanation?`<p class="subtle"><b>AI:</b> ${escapeHtml(o.explanation)}</p>`:''}${o.unresolved?.length?`<p class="subtle"><b>Open questions:</b> ${o.unresolved.map(escapeHtml).join(' · ')}</p>`:''}`;}
function renderArch(data){
 pipe.archData=data;const el=$('arch-view');if(!el)return;const sp=data.spec;
 el.innerHTML=`<div class="arch-label">ARCHITECTURES · ${sp.size} × ${sp.size} INT8 → INT32 · same RTL source, two parameter choices</div><div class="arch-cards">${data.candidates.map(c=>{const b=pipe.builds?.[c.lanes],ready=b&&sp.size===8;
  return `<div class="arch-card ${c.within_lane_limit?'':'excluded'}"><div class="arch-title">${swatch(c.lanes)}<b>${c.lanes===1?'1 lane · Sequential MAC':'4 lanes · Parallel MAC array'}</b>${c.within_lane_limit?'':'<span class="tag">OVER LANE LIMIT</span>'}</div><p>${c.lanes===1?'One multiply-accumulate unit computes one output at a time.':'Four multiply-accumulate units compute four output columns at once.'}</p><div class="lane-diagram" aria-label="${c.lanes} arithmetic lanes"><span class="lane-port">A,B</span><span class="lane-link"></span>${'<span class="lane">MAC</span>'.repeat(c.lanes)}<span class="lane-link"></span><span class="lane-port">C</span></div><div class="kvs">${kv('Model cycles',pfmt(c.cycles))}${kv(`At ${sp.frequency_mhz} MHz`,`${c.projected_us.toFixed(2)} <em>µs · projected</em>`)}</div><p class="hash">${ready?`✓ KV260 bitstream ready · built in Vivado ${escapeHtml(b.vivado)} on ${escapeHtml(new Date(b.build_started_at).toLocaleDateString())}`:sp.size!==8?'Simulation only: KV260 bitstreams exist for 8 × 8.':'Checking for a KV260 bitstream…'}</p></div>`;}).join('')}</div>`;
}
function showSpecStep(){pipe.specShown=true;renderPipeline();developDiagram(readSpec());}
function onExplore(data){pipe.archData=data;renderPipeline();if(pipe.specShown||pipe.mode)developDiagram(data.spec);}

// ---------------------------------------------------------------- 03 block diagram
// Ported from Christopher's architecture map + RTL schematic (codex/demo-pipeline eb16f64). Topology comes only from
// the validated catalog plan (/api/plan, deterministic, no AI). Kept outside resetPipe: it depends on the spec, not a run.
const diag={key:null,plans:{},status:'waiting',error:null,show:null,req:0,painted:null};
const specKey=s=>JSON.stringify(s,Object.keys(s).sort());
async function developDiagram(spec){
 if(!spec)return;const key=specKey(spec);if(diag.key===key&&diag.status!=='failed')return;
 const req=++diag.req,lanes=[1,4].filter(l=>l<=spec.max_lanes);Object.assign(diag,{key,plans:{},status:'running',error:null});renderPipeline();
 try{const plans=await Promise.all(lanes.map(l=>api('/api/plan',{spec,lanes:l})));if(req!==diag.req)return;
  for(const p of plans)if(p.evidence!=='build_plan'||!p.parameters||p.parameters.N!==spec.size||!lanes.includes(p.parameters.LANES))throw new Error('the server did not return a matching validated plan.');
  diag.plans=Object.fromEntries(plans.map(p=>[p.parameters.LANES,p]));if(!diag.plans[diag.show])diag.show=Math.max(...lanes);diag.status='done';
 }catch(e){if(req!==diag.req)return;diag.status='failed';diag.error='Block diagram unavailable: '+e.message;}
 renderPipeline();
}
function schematicHtml(plan){const lanes=plan.parameters.LANES,n=plan.parameters.N,shape=(plan.block_id.split('.')[2]||'').toUpperCase(),laneCards=Array.from({length:lanes},(_,i)=>`<div class="schematic-lane"><span>LANE ${i+1}</span><strong>8b × 8b → 16b</strong><small>signed multiply</small><b>＋</b><strong>32-bit acc</strong></div>`).join('');
 return `<div class="schematic" role="img" aria-label="RTL data path: signed INT8 A and B operand arrays feed ${lanes} multiplier and INT32 accumulator lane${lanes>1?'s':''}; results go to the C output array. Row, column, and k counters sequence the lanes."><div class="schematic-title"><span>RTL DATA PATH / ${n} × ${n}</span><span>${lanes} LANE${lanes>1?'S':''} · ${escapeHtml(shape)}</span></div><div class="schematic-grid"><div class="schematic-inputs"><div class="schematic-block"><small>OPERAND A</small><strong>INT8 array</strong><span>${n} × ${n} signed values</span></div><div class="schematic-block"><small>OPERAND B</small><strong>INT8 array</strong><span>${n} × ${n} signed values</span></div></div><div class="schematic-wire"><span>A[row, k]<br>B[k, col${lanes>1?' + lane':''}]</span></div><div class="schematic-compute"><small>${lanes>1?'PARALLEL':'SEQUENTIAL'} COMPUTE · ${lanes} ×</small><div class="schematic-lanes${lanes===1?' one':''}">${laneCards}</div></div><div class="schematic-wire"><span>INT32 results</span></div><div class="schematic-block schematic-output"><small>OUTPUT C</small><strong>INT32 array</strong><span>${n} × ${n} results</span></div></div><div class="schematic-control"><span>CONTROL PATH</span><strong>row · col · k counters</strong><span>start → busy → done</span><span>One reduction step per active cycle; output written at k = N − 1</span></div><p class="schematic-caption">Source shape: checked-in <code>hardware/matmul.sv</code> with N=${n}, LANES=${lanes}. Arrays are RTL storage, not a BRAM mapping claim. Host loading and board integration are outside this compute path.</p></div>`;}
function diagramHtml(){
 const L=Object.keys(diag.plans).map(Number).sort((a,b)=>a-b),plan=diag.plans[diag.show],spec=plan.spec,n=plan.parameters.N,lanes=plan.parameters.LANES,onBoard=n===8;
 const toggle=L.length>1?`<div class="diagram-toggle" role="group" aria-label="Architecture shown in the diagram">${L.map(l=>`<button type="button" data-diagram="${l}" class="${l===lanes?'active':''}" aria-pressed="${l===lanes}">${swatch(l)}${laneName(l)}</button>`).join('')}</div>`:'';
 const flow=`<div class="architecture-flow" role="img" aria-label="Flow from the reviewed specification through ${laneName(lanes)} to ${onBoard?'the KV260':'simulation'}"><div class="architecture-node intent"><small>REVIEWED INPUT</small><strong>Requirement &amp; constraints</strong><span>${spec.objective==='minimize_latency'?'Prefer lower modeled compute cycles':'Prefer fewer arithmetic lanes'} · lane limit ${escapeHtml(spec.max_lanes)}</span></div><span class="architecture-arrow">→</span><div class="architecture-node config"><small>VALIDATED CONFIG</small><strong>N=${n} · INT8 → INT32</strong><span>${laneName(lanes)} · ${escapeHtml(spec.frequency_mhz)} MHz requested</span></div><span class="architecture-arrow">→</span><div class="architecture-node compute"><small>CATALOG RTL SHAPE</small><strong>${lanes===1?'Sequential compute lane':'Parallel compute lanes'}</strong><div class="architecture-lanes">${Array.from({length:lanes},(_,i)=>`<span class="architecture-lane">MAC ${i+1}</span>`).join('')}</div></div><span class="architecture-arrow">→</span><div class="architecture-node integration"><small>${onBoard?'ON THE KV260':'SIMULATION ONLY'}</small><strong>${onBoard?'Zynq PS → AXI4-Lite → matmul_axi':'Icarus Verilog'}</strong><span>${onBoard?'Loaded and read over JTAG · registers at 0xA0000000 · PS clock pl_clk0 ≈ 100 MHz':'KV260 bitstreams exist for 8 × 8 only'}</span></div></div>`;
 return `<article class="architecture-map-card"><div class="architecture-map-head"><div><span class="eyebrow">VALIDATED CATALOG PLAN · ${escapeHtml(plan.block_id)}</span><h3>${n} × ${n} signed INT8 matrix multiply · ${laneName(lanes)}</h3></div><div class="diagram-head-right">${toggle}<span class="tag">CONCEPTUAL · NOT VIVADO</span></div></div>${flow}${schematicHtml(plan)}<div class="architecture-map-foot"><p>Recipe SHA-256 ${pshort(plan.recipe_sha256)} · source <code>matmul.sv</code> ${pshort(plan.source_sha256?.['hardware/matmul.sv'])} · ${escapeHtml(plan.selection||'deterministic catalog selection')}. A plan, not evidence: simulation, Vivado and the board come next.</p></div></article>`;
}
function renderDiagram(box){
 const key=[diag.key,diag.status,diag.show,diag.error].join('|');if(diag.painted===key&&box.innerHTML)return;diag.painted=key;
 if(diag.status==='failed'){box.innerHTML=`<p class="bad-line">${escapeHtml(diag.error)}</p>`;return;}
 if(diag.status!=='done'||!diag.plans[diag.show]){box.innerHTML='<p class="subtle">Developing the block diagram from the validated catalog recipe…</p>';return;}
 box.innerHTML=diagramHtml();
 document.querySelectorAll('[data-diagram]').forEach(b=>b.onclick=()=>{diag.show=Number(b.dataset.diagram);renderPipeline();});
}

// ---------------------------------------------------------------- 03 RTL
function rtlArtifact(){
 const L=pLanes();if(!L.length)return '';const first=pipe.sims[L[0]];const src=(first.source_files?.['matmul.sv']||'').split('\n');
 const head=first.source_files?.['matmul.sv']?`<div class="artifact"><div class="artifact-head"><b>hardware/matmul.sv</b> · SHA-256 ${pshort(first.source_sha256?.['matmul.sv'])} · one parameterized module, N and LANES set per architecture</div><pre class="code">${escapeHtml(src.slice(0,16).join('\n'))}\n…  (${src.length} lines)</pre></div>`:'';
 const cards=L.map(l=>{const r=pipe.sims[l],h=pipe.handoffs[l],out=(r.simulator_stdout||'').split('\n').filter(x=>x.startsWith('CYCLES')||x.startsWith('OUT')).slice(0,4).join('\n');
  return `<div class="lane-card"><h4>${swatch(l)}${laneName(l)} · simulation run ${escapeHtml(r.id.slice(0,8))}</h4><div class="kvs">${kv('Simulated cycles',pfmt(r.cycles))}${kv('Outputs vs reference',`${r.outputs.length}/${r.outputs.length} ✓`,'good')}${kv('Simulator',escapeHtml((r.simulator||'').replace('Icarus Verilog version','Icarus').split(' (')[0]))}</div>${out?`<pre class="code small">${escapeHtml(out)}\n…</pre>`:''}${h?`<p class="hash">FPGA handoff ZIP: ${h.files.length} files (${h.files.filter(f=>f.sha256).map(f=>escapeHtml(f.name.split('/').pop())).slice(0,5).join(', ')}, …), each SHA-256 fingerprinted · <a class="linklike" href="/api/runs/${escapeHtml(r.id)}/handoff.zip" download>download</a></p>`:''}</div>`;});
 return head+laneGrid(cards);
}
// ---------------------------------------------------------------- 04 Vivado
function vivadoArtifact(){
 if(!pipe.builds)return '';const L=(pLanes().length?pLanes():[1,4]).filter(l=>pipe.builds[l]);
 return laneGrid(L.map(l=>{const b=pipe.builds[l],t=b.timing,a=b.area,p=b.power,sim=pipe.sims[l];
  const match=sim?sim.source_sha256?.['matmul.sv']===b.rtl_sha256['matmul.sv']:b.rtl_matches_app;const ex=pipe.excerpts[l];
  return `<div class="lane-card"><h4>${swatch(l)}${laneName(l)} · ${escapeHtml(b.bitstream)}</h4><p class="subtle">Vivado ${escapeHtml(b.vivado)} · ${escapeHtml(b.part)} · synthesis + place &amp; route + bitstream in ${b.build_minutes} min (${escapeHtml(new Date(b.build_started_at).toLocaleString())})</p>
   <p class="${match?'ok-line':'bad-line'}">${match?'✓ Built from exactly this RTL (SHA-256 match), so the bitstream is reused, not rebuilt.':'✗ This RTL does not match the bitstream.'}</p>
   <div class="kvs">${kv('Timing @ 100 MHz',t.met?`MET <em>slack +${t.WNS_ns} ns</em>`:'NOT MET',t.met?'good':'bad')}${kv('Fmax estimate',`≈${pfmt(t.fmax_estimate_mhz)} <em>MHz</em>`)}${kv('LUTs · FFs',`${pfmt(a['Total LUTs'])} <em>· ${pfmt(a.FFs)}</em>`)}${kv('DSP · BRAM',`${pfmt(a['DSP Blocks'])} <em>· ${pfmt(a.RAMB36+a.RAMB18)}</em>`)}${kv('Power estimate',`${p.kernel_w} <em>W matmul</em>`)}${kv('Design rules',b.drc_clean?'DRC clean':'DRC issues',b.drc_clean?'good':'bad')}</div>
   ${ex?`<pre class="code small" aria-label="Excerpt of timing_summary.rpt">${escapeHtml(ex)}</pre>`:''}
   <p class="report-links">${b.reports.map(rp=>`<a href="/api/fpga/builds/${b.lanes}/reports/${escapeHtml(rp.name)}" target="_blank" rel="noopener">${rp.verified?'✓':'✗'} ${escapeHtml(rp.name)}</a>`).join('')}</p></div>`;}));
}
function timingExcerpt(text){const lines=text.split(/\r?\n/);const i=lines.findIndex(x=>x.startsWith('| Design Timing Summary'));if(i<0)return null;const met=lines.slice(i,i+14).find(x=>/timing constraints are (met|not met)/.test(x))||'';const table=lines.slice(i+4,i+7).map(x=>x.replace(/\s+$/,'').slice(0,96));return ['timing_summary.rpt  (excerpt)',...table,'',met.trim()].join('\n');}
// ---------------------------------------------------------------- 05 KV260
function transcriptExcerpt(text){return text.split(/\r?\n/).filter(x=>x.startsWith('MM ')).map(x=>{if(x.startsWith('MM OUT ')){const p=x.split(' ');return `${p.slice(0,3).join(' ')} ${p.slice(3,9).join(' ')} … (${p.length-3} values)`;}return x.replace(/ host_ns=\d+/,'');}).join('\n');}
// The board scene (illustration + JTAG chain) sits outside art-board so its animations are not restarted by the
// once-a-second job polling re-render; it repaints only when its content key changes.
function sceneState(){const s=pipe.status,c=pipe.check;if(s.board==='running')return 'checking';if(s.run==='running'||s.import==='running')return 'running';if(!c)return 'unknown';if(c.recorded)return 'recorded';if(c.available)return 'connected';return c.cable_serial?'nopower':'unplugged';}
const SCENE_HEAD={checking:['Scanning JTAG for the KV260…','Read-only: finds the cable and the chips, programs nothing.'],connected:['KV260 connected','Found by a read-only JTAG scan'],running:['Running on the KV260',''],recorded:['Recorded KV260 run (not live)',''],unplugged:['USB-JTAG cable not found','Plug the micro-USB cable into J4, then build again.'],nopower:['Cable found, but the board did not answer','Check 12 V power on J12 and close Vivado Hardware Manager, then build again.'],unknown:['Board not checked','']};
function boardSceneHtml(st){
 const c=pipe.check||{},devs=c.devices||[],has=re=>devs.some(d=>re.test(d)),job=Object.values(pipe.jobs).find(j=>j.status==='running');
 let [title,sub]=SCENE_HEAD[st];
 if(st==='connected'&&c.checked_at)sub+=' at '+new Date(c.checked_at).toLocaleTimeString();
 if(st==='running'&&job)sub=`${laneName(job.lanes)}: ${job.message}`;
 if(st==='recorded')sub=`From the saved board result, not a live scan. The accelerator answered with identity ${c.identity}.`;
 const nodes=st==='recorded'?[['This laptop','recorded run','ok'],['USB-JTAG cable',c.cable_serial||'—','ok'],['matmul_axi',`identity ${c.identity} (“SIL”)`,'ok']]
  :[['This laptop','xsdb + hw_server','ok'],['USB-JTAG cable',c.cable_serial||'not found',c.cable_serial?'ok':'miss'],['xck26','FPGA · runs the accelerator',has(/xck26/)?'ok':'miss'],['arm_dap','Zynq processor debug port · drives AXI',has(/arm_dap/)?'ok':'miss']];
 if(st==='checking')nodes.slice(1).forEach(x=>{x[2]='pending';});
 return `<div class="board-headline"><span class="board-dot"></span><div><strong>${escapeHtml(title)}</strong>${sub?`<small>${escapeHtml(sub)}</small>`:''}</div></div><ol class="jtag-chain" aria-label="JTAG chain">${nodes.map(([n,d,s])=>`<li class="${s}"><i aria-hidden="true">${s==='ok'?'✓':s==='miss'?'✗':''}</i><b>${escapeHtml(n)}</b><span>${escapeHtml(d)}</span></li>`).join('')}</ol>${(st==='unplugged'||st==='nopower')&&c.reason?`<p class="subtle">JTAG check: ${escapeHtml(c.reason)}</p>`:''}`;
}
function renderBoardScene(){
 const side=$('board-side');if(!side)return;const st=sceneState(),job=Object.values(pipe.jobs).find(j=>j.status==='running');
 paintBoard($('board-visual-big'),st,SCENE_HEAD[st][0]);if($('board-scene'))$('board-scene').setAttribute('data-state',st);
 const key=JSON.stringify([st,pipe.check,job&&[job.lanes,job.message]]);if(pipe.scenePainted===key)return;pipe.scenePainted=key;side.innerHTML=boardSceneHtml(st);
}
function boardArtifact(){
 let html='';
 const L=pLanes().filter(l=>pipe.jobs[l]||pipe.boards[l]);
 if(L.length)html+=laneGrid(L.map(l=>{const j=pipe.jobs[l],c2=pipe.boards[l];
  if(!c2){const tail=(j?.log||[]).filter(x=>x.trim()&&!x.startsWith('>')).slice(-2).join('\n');return `<div class="lane-card"><h4>${swatch(l)}${laneName(l)}</h4><p>${j.status==='failed'?'✗ '+escapeHtml(j.error||'Failed'):escapeHtml(j.message)+` · ${pfmt(Math.round(j.elapsed_s||0))} s`}</p>${j.status==='running'?'<div class="progress-bar"><span></span></div>':''}${tail?`<pre class="code small">${escapeHtml(tail)}</pre>`:''}</div>`;}
  const ic=c2.interface_check||{},bi=c2.board_import||{},folder=c2.runner_result_folder||j?.result_folder,tr=pipe.transcripts[l];
  return `<div class="lane-card"><h4>${swatch(l)}${laneName(l)} · ran on the chip</h4><div class="kvs">${kv('Measured cycles',pfmt(c2.cycles),'good')}${kv('Outputs match',`${c2.outputs.length}/${c2.outputs.length}`,'good')}${kv('Repeat · reset + rerun','✓ · ✓')}${kv('FPGA programmed in',`${(c2.programming_elapsed_ns/1e9).toFixed(1)} <em>s</em>`)}</div>${tr?`<pre class="code small" aria-label="JTAG transcript excerpt">${escapeHtml(tr)}</pre>`:''}<p class="hash">Identity register 0x${Number(ic.identity||0).toString(16).toUpperCase()} (“SIL”) · chip reports N=${escapeHtml(ic.compiled_n)}, LANES=${escapeHtml(ic.compiled_lanes)} · JTAG transfer ${(c2.host_elapsed_ns/1e9).toFixed(1)} s (debug link, not accelerator speed)</p><p class="hash">✓ Signed (HMAC-SHA256, key <code>${escapeHtml(bi.key_id||'?')}</code>) and accepted after matching the simulation: sources, inputs, all ${c2.outputs.length} outputs, cycles, bitstream and report hashes · saved as board run ${escapeHtml(c2.id.slice(0,8))}</p><p class="report-links">${folder?`<a href="/api/board/results/${escapeHtml(folder)}/xsdb.log" target="_blank" rel="noopener">Full JTAG transcript</a><a href="/api/board/results/${escapeHtml(folder)}/board-result.json" target="_blank" rel="noopener">board-result.json</a>`:''}<button class="linklike" data-view-run="${escapeHtml(c2.id)}">Inspect board run ↗</button></p></div>`;}));
 return html;
}
// ---------------------------------------------------------------- 06 results
function chartPanel(title,note,values,fmt){const max=Math.max(...values.map(v=>v[1]||0));return `<div class="chart-panel"><div class="chart-title">${title}<small>${note}</small></div>${values.map(([l,v])=>`<div class="chart-row" title="${laneName(l)}: ${escapeHtml(fmt(v))}"><span class="chart-label">${laneName(l)}</span><span class="chart-track"><span class="chart-bar" style="width:${max?Math.max(1.5,100*v/max):0}%;background:${SERIES[l]}"></span></span><span class="chart-value">${escapeHtml(fmt(v))}</span></div>`).join('')}</div>`;}
function resultsArtifact(){
 const L=pLanes();if(!L.length)return '';
 const b=pipe.boards,B=pipe.spec&&pipe.spec.size!==8?{}:(pipe.builds||{}),measured=L.every(l=>b[l]);
 const cyc=l=>(b[l]||pipe.sims[l]).cycles,lut=l=>B[l]?.area['Total LUTs'];
 let head='';
 if(L.length===2){const speed=(cyc(1)/cyc(4)).toFixed(2),area=lut(1)&&lut(4)?(lut(4)/lut(1)).toFixed(1):null;
  head=`<div class="compare-head"><div class="hero"><strong>${speed}×</strong><span>fewer kernel cycles${measured?', measured on the KV260':' in simulation'}</span></div>${area?`<div class="hero"><strong>${area}×</strong><span>the matmul LUTs (area cost)</span></div>`:''}<div class="hero"><strong>${pipe.sims[L[0]].outputs.length}/${pipe.sims[L[0]].outputs.length}</strong><span>outputs identical on both</span></div></div>`;}
 const panels=[chartPanel(`Kernel cycles${measured?' · measured on the KV260':' · simulated'}`,'lower is faster',L.map(l=>[l,cyc(l)]),v=>pfmt(v))];
 if(L.every(l=>B[l]))panels.push(chartPanel('Matmul LUTs','area · Vivado report',L.map(l=>[l,lut(l)]),v=>pfmt(v)),chartPanel('Flip-flops','area · Vivado report',L.map(l=>[l,B[l].area.FFs]),v=>pfmt(v)),chartPanel('Fmax estimate','MHz · higher is faster · 100 MHz used',L.map(l=>[l,B[l].timing.fmax_estimate_mhz]),v=>`≈${v} MHz`));
 const legend=`<div class="chart-legend">${L.map(l=>`<span>${swatch(l)}${laneName(l)}</span>`).join('')}</div>`;
 const rows=[['Simulated cycles (Icarus)',l=>pfmt(pipe.sims[l]?.cycles)],['Measured cycles (KV260 counter)',l=>b[l]?pfmt(b[l].cycles):'—'],['Kernel time at 99.999 MHz (calculated)',l=>b[l]?b[l].kernel_time_us.toFixed(2)+' µs':'—'],['Outputs verified on the board',l=>b[l]?`${b[l].outputs.length}/${b[l].outputs.length}`:'—'],['LUTs (matmul)',l=>pfmt(B[l]?.area['Total LUTs'])],['Flip-flops',l=>pfmt(B[l]?.area.FFs)],['DSP · BRAM',l=>B[l]?`${B[l].area['DSP Blocks']} · ${B[l].area.RAMB36+B[l].area.RAMB18}`:'—'],['Timing slack (WNS)',l=>B[l]?`+${B[l].timing.WNS_ns} ns`:'—'],['Fmax estimate',l=>B[l]?`≈${B[l].timing.fmax_estimate_mhz} MHz`:'—'],['Matmul power (Vivado estimate)',l=>B[l]?`${B[l].power.kernel_w} W`:'—']];
 const table=`<details class="table-view" data-key="results-table" open><summary>All numbers</summary><table class="cell-table compare-table"><thead><tr><th scope="col">Metric</th>${L.map(l=>`<th scope="col">${laneName(l)}</th>`).join('')}</tr></thead><tbody>${rows.map(([k,f])=>`<tr><td>${k}</td>${L.map(l=>`<td>${f(l)}</td>`).join('')}</tr>`).join('')}</tbody></table></details>`;
 return `<div class="artifact results">${head}${legend}<div class="chart-grid">${panels.join('')}</div>${table}<p class="subtle">Four lanes buy speed with more logic; this is arithmetic capacity, not a free speedup. Kernel time is cycles ÷ the configured clock, not a stopwatch time; JTAG transfer and programming times are not accelerator speed; power is a Vivado estimate.${pipe.spec&&pipe.spec.size!==8?' Vivado and board figures exist only for 8 × 8, so they are left out here.':''}</p></div>`;
}
const ARTIFACTS={rtl:rtlArtifact,vivado:vivadoArtifact,board:boardArtifact,results:resultsArtifact};

// ---------------------------------------------------------------- rendering
function renderPipeline(){
 const prog=$('flow-progress');
 if(prog)prog.innerHTML=FLOW.filter(([k])=>!(state.publicDemo&&pipe.mode==='live'&&k==='board')).map(([k,label],i)=>`<li class="${flowStatus(k)}"><a href="#step-${k}"><b>${flowStatus(k)==='done'?'✓':String(i+1).padStart(2,'0')}</b>${label}</a></li>`).join('');
 if($('spec-origin'))$('spec-origin').textContent=specOriginText();
 if($('spec-notes'))$('spec-notes').innerHTML=specNotes();
 if($('step-spec'))$('step-spec').hidden=!(pipe.specShown||pipe.mode);
 if(pipe.archData)renderArch(pipe.archData);
 let reveal=null;
 for(const [k] of FLOW.slice(2)){const art=$('step-'+k),st=flowStatus(k),err=flowError(k);if(!art)continue;if(state.publicDemo&&pipe.mode==='live'&&k==='board'){art.hidden=true;continue;}
  const show=st!=='waiting';art.hidden=!show;art.className='flow-step '+st;
  if($('chip-'+k))$('chip-'+k).innerHTML=chip(st);
  if(show&&k==='diagram'){try{renderDiagram($('art-diagram'));}catch(e){$('art-diagram').innerHTML=`<p class="bad-line">Could not display the block diagram: ${escapeHtml(e.message)}</p>`;diag.painted=null;}}
  else if(show){const box=$('art-'+k),open=new Set((box.querySelectorAll?[...box.querySelectorAll('details[open]')]:[]).map(d=>d.dataset?.key));let body='';try{body=st==='skipped'?'':ARTIFACTS[k]();}catch(e){body=`<p class="bad-line">Could not display this step: ${escapeHtml(e.message)}</p>`;}
   box.innerHTML=(err?`<p class="bad-line">${escapeHtml(err)}</p>`:'')+body;if(box.querySelectorAll)box.querySelectorAll('details').forEach(d=>{if(d.dataset?.key&&open.has(d.dataset.key))d.open=true;});
   if(!pipe.revealed.has(k)){pipe.revealed.add(k);reveal=art;}}}
 if(flowStatus('board')!=='waiting'&&!(state.publicDemo&&pipe.mode==='live'))renderBoardScene();
 renderBoardState();
 if(reveal&&pipe.mode==='live'&&reveal.scrollIntoView)reveal.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
 const fin=$('live-final');if(fin)fin.innerHTML=pipe.note?`<p class="notice">${escapeHtml(pipe.note)}</p>`:'';
 const run=$('live-run');if(run){run.disabled=state.busy||!state.simulator;run.textContent=pipe.running?'Running…':state.publicDemo?'▶ Run RTL simulations & inspect saved build reports':'▶ Build it and run it on the KV260';}
 for(const id of ['live-check','live-recorded'])if($(id))$(id).disabled=state.busy||state.publicDemo;
 if(typeof bindRunLinks==='function')bindRunLinks();
}

// ---------------------------------------------------------------- actions
async function loadBuilds(){try{const b=await api('/api/fpga/builds');pipe.builds=Object.fromEntries(b.builds.map(x=>[x.lanes,x]));}catch(e){}}
async function checkBoardNow(){if(state.busy||state.publicDemo)return;state.boardActivity='checking';setBusy(true);notice('Scanning JTAG for the KV260 (read-only)…');try{const c=await api('/api/board/check',{});state.board=c.available;state.boardDetails=c;state.boardActivity=null;notice(c.available?'KV260 connected: '+c.cable_serial:'KV260 not detected: '+(c.reason||''),!c.available);}catch(e){notice(e.message,true);}finally{state.boardActivity=null;setBusy(false);}}
async function generateSpec(){
 if(state.busy||!state.ai)return;const b=$('generate');setBusy(true);b.textContent='Drafting the specification…';notice('Asking the AI to turn your prompt into a hardware specification…');
 try{const draft=await api('/api/spec',{prompt:$('prompt').value,target:'kv260'});
  if(!draft.supported){notice('Not supported: '+(draft.explanation||'this workload is outside the supported matrix-multiply family.'),true);return;}
  const checked=await api('/api/explore',{spec:draft.spec});
  fillSpec(checked.spec,draft.provenance,{kind:'ai',prompt:$('prompt').value,explanation:draft.explanation,unresolved:draft.unresolved||[],model:state.aiDetails.model||null});
  resetPipe(null);showSpecStep();await explore();notice('AI specification ready. Review it, then build.');
  if($('step-spec')?.scrollIntoView)$('step-spec').scrollIntoView({behavior:'smooth',block:'start'});
 }catch(e){notice(e.message,true);}finally{setBusy(false);b.innerHTML='Generate specification <span>↗</span>';}
}
async function useExample(){
 if(state.busy)return;const spec={operation:'matrix_multiply',size:8,precision:'int8',target:'kv260',frequency_mhz:100,max_dsps:16,max_lanes:4,objective:'minimize_latency'};
 fillSpec(spec,Object.fromEntries(Object.keys(spec).map(k=>[k,'built-in example'])),{kind:'example'});
 resetPipe(null);showSpecStep();await explore();notice('Loaded the built-in 8 × 8 INT8 example. Review it, then build.');
 if($('step-spec')?.scrollIntoView)$('step-spec').scrollIntoView({behavior:'smooth',block:'start'});
}
async function runPipeline(){
 if(state.busy||pipe.running||!$('spec-form').reportValidity())return;
 const spec=readSpec(),lanes=spec.max_lanes>=4?[1,4]:[1];
 resetPipe('live');pipe.specShown=true;pipe.spec=spec;pipe.origin={...state.specOrigin};pipe.running=true;pipe.startedAt=Date.now();developDiagram(spec);
 setBusy(true);let current='sim';
 const step=(k,s)=>{if(s==='running')current=k;pipe.status[k]=s;renderPipeline();};
 try{
  step('sim','running');
  for(const l of lanes){notice(`Simulating the ${laneName(l)} RTL in Icarus Verilog…`);pipe.sims[l]=await api('/api/simulate',{spec,lanes:l,seed:42});renderPipeline();}
  step('handoff','running');
  for(const l of lanes)pipe.handoffs[l]=await api(`/api/runs/${pipe.sims[l].id}/handoff.json`);
  step('sim','done');step('handoff','done');
  if(spec.size!==8){for(const k of ['vivado','board','run','import'])pipe.status[k]='skipped';pipe.error.vivado='The saved KV260 bitstreams were built for 8 × 8 only. This 16 × 16 run stops after simulation.';step('compare','done');pipe.note='Simulation complete. Saved Vivado reports are available only for matching 8 × 8 RTL. A live board run requires the separate runner.';return;}
  await psleep(STEP_DWELL_MS);
  step('vivado','running');notice('Re-checking each bitstream and its Vivado reports against this RTL…');
  await Promise.all([loadBuilds(),psleep(900)]);if(!pipe.builds){if(state.publicDemo){pipe.status.vivado='skipped';pipe.status.board='skipped';pipe.status.run='skipped';pipe.status.import='skipped';step('compare','done');pipe.note='RTL simulation complete. Saved Vivado build reports are unavailable on this host; live board measurements require the separate KV260 runner.';notice(pipe.note);return;}throw stepError('vivado','Vivado build evidence is unavailable.');}
  for(const l of lanes){const b=pipe.builds[l];if(!b||b.rtl_sha256['matmul.sv']!==pipe.sims[l].source_sha256['matmul.sv']||!b.bitstream_verified||!b.timing.met||!b.drc_clean||!b.reports.every(r=>r.verified))throw stepError('vivado',`The ${laneName(l)} bitstream was not built from this RTL, or its files changed. A new Vivado build would be needed.`);
   try{pipe.excerpts[l]=timingExcerpt(await fetchText(`/api/fpga/builds/${l}/reports/timing_summary.rpt`));}catch(_){}}
  step('vivado','done');
  if(state.publicDemo){for(const k of ['board','run','import'])pipe.status[k]='skipped';step('compare','done');pipe.elapsed=Math.round((Date.now()-pipe.startedAt)/1000);pipe.note='RTL simulations passed and matching saved Vivado reports were checked. Live board measurements require the separate KV260 runner; signed board-result import is unavailable in this hosted demo.';notice(pipe.note);return;}
  await psleep(STEP_DWELL_MS);
  state.boardActivity='checking';step('board','running');notice('Scanning JTAG for the KV260 (read-only)…');
  pipe.check=await api('/api/board/check',{});state.board=pipe.check.available;state.boardDetails=pipe.check;state.boardActivity=null;
  if(!pipe.check.available)throw stepError('board',(pipe.check.reason||'KV260 not detected')+'. Check J4 (micro-USB) and J12 (12 V), close Vivado Hardware Manager, then build again.');
  state.boardActivity='running';step('board','done');step('run','running');
  for(const l of lanes){
   notice(`Programming the KV260 with the ${laneName(l)} bitstream and running the job…`);
   let job=await api(`/api/runs/${pipe.sims[l].id}/board-run`,{});pipe.jobs[l]=job;renderPipeline();
   while(job.status==='running'){await psleep(1000);job=await api('/api/board/jobs/'+job.id);pipe.jobs[l]=job;if(['sign','import'].includes(job.stage)&&pipe.status.import!=='running')step('import','running');else renderPipeline();}
   if(job.status!=='done')throw stepError(['sign','import'].includes(job.stage)?'import':'run',job.error||'Board run failed');
   pipe.boards[l]=await api('/api/runs/'+job.child_id);
   const folder=pipe.boards[l].runner_result_folder||job.result_folder;
   if(folder){try{pipe.transcripts[l]=transcriptExcerpt(await fetchText(`/api/board/results/${folder}/xsdb.log`));}catch(_){}}
   renderPipeline();
  }
  step('run','done');step('import','done');step('compare','done');
  pipe.elapsed=Math.round((Date.now()-pipe.startedAt)/1000);
  pipe.note=`Pipeline complete in ${pipe.elapsed} s. Board runs ${lanes.map(l=>pipe.boards[l].id.slice(0,8)).join(' and ')} are saved under Run history.`;
  notice('Done: both architectures ran on the KV260 and every output matched the simulation.');
 }catch(e){pipe.status[e.step||current]='failed';pipe.error[e.step||current]=e.message;notice(e.message,true);}
 finally{pipe.running=false;state.boardActivity=null;setBusy(false);try{await history();}catch(_){}renderPipeline();}
}
async function showRecorded(){
 if(state.busy||pipe.running||state.publicDemo)return;
 try{
  const runs=await api('/api/runs');state.runs=runs;
  const boards=runs.filter(r=>r.evidence==='board_measured');let pair=null;
  for(const b of boards){const o=boards.find(x=>x.lanes!==b.lanes&&x.input_sha256===b.input_sha256);if(o){pair=b.lanes===1?[b,o]:[o,b];break;}}
  if(!pair){notice('No recorded pair of 1-lane and 4-lane board runs yet. Build and run first.',true);return;}
  resetPipe('recorded');
  const kids=await Promise.all(pair.map(c=>api('/api/runs/'+c.id)));
  const sims=await Promise.all(kids.map(c=>api('/api/runs/'+c.parent_run_id)));
  kids.forEach(c=>{pipe.boards[c.lanes]=c;});sims.forEach(s=>{pipe.sims[s.lanes]=s;});
  for(const s of sims){try{pipe.handoffs[s.lanes]=await api(`/api/runs/${s.id}/handoff.json`);}catch(_){}}
  await loadBuilds();
  for(const l of [1,4]){try{pipe.excerpts[l]=timingExcerpt(await fetchText(`/api/fpga/builds/${l}/reports/timing_summary.rpt`));}catch(_){}
   const f=pipe.boards[l]?.runner_result_folder;if(f){try{pipe.transcripts[l]=transcriptExcerpt(await fetchText(`/api/board/results/${f}/xsdb.log`));}catch(_){}}}
  pipe.spec=sims[0].spec;pipe.specShown=true;state.specOrigin={kind:'recorded'};
  pipe.check={recorded:true,cable_serial:kids[0].board?.jtag_cable_serial,identity:'0x'+Number(kids[0].interface_check?.identity||0).toString(16).toUpperCase()};
  for(const k of ['sim','handoff','vivado','board','run','import','compare'])pipe.status[k]='done';
  pipe.note=`Recorded real run (not live): board runs ${kids.map(c=>c.id.slice(0,8)).join(' and ')}, recorded ${new Date(kids[0].recorded_at).toLocaleString()}.`;
  renderPipeline();developDiagram(pipe.spec);notice('Showing the last recorded board runs. They are labelled as recorded, not live.');
 }catch(e){notice(e.message,true);}
}
if($('generate'))$('generate').onclick=generateSpec;
if($('sample'))$('sample').onclick=useExample;
if($('live-run'))$('live-run').onclick=runPipeline;
if($('live-check'))$('live-check').onclick=checkBoardNow;
if($('live-recorded'))$('live-recorded').onclick=showRecorded;
loadBuilds().then(renderPipeline);
