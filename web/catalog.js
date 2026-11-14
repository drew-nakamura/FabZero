// Separate catalog module preserves the existing workbench's interaction flow.
(()=>{
 const section=document.createElement('section');section.className='evidence';section.id='block-catalog';
 section.innerHTML='<div class="section-heading"><div><div class="eyebrow">REUSABLE RTL</div><h2>Build from inspected blocks.</h2></div><button class="button dark" id="build-recipe" data-build>Build verified design →</button><button class="button outline" id="export-recipe">↓ Build recipe</button></div><p class="subtle">The current specification selects a verified compute recipe. Upstream utilities remain separate until integration is tested. Recipe export uses no AI tokens.</p><div id="catalog-items" class="candidate-grid"></div><progress id="build-progress" hidden aria-label="Verifying design" style="width:100%;accent-color:var(--green)"></progress><p id="catalog-status" role="status"></p>';
 document.getElementById('method').before(section);
 const status=section.querySelector('#catalog-status');
 fetch('/api/catalog').then(r=>{if(!r.ok)throw Error('Catalog unavailable');return r.json();}).then(data=>{
  for(const block of data.blocks){const card=document.createElement('article');card.className='candidate';const title=document.createElement('h3');title.textContent=block.id;title.style.overflowWrap='anywhere';const description=document.createElement('p');description.textContent=block.qualification;const badge=document.createElement('span');badge.className='tag';badge.textContent=block.runnable?'COMPUTE RECIPE':'STANDALONE UTILITY';const credit=document.createElement('p');credit.className='subtle';credit.textContent='License: '+block.license+(block.commit?' · Upstream '+block.commit.slice(0,12):' · SiliconOS');card.append(title,badge,description,credit);section.querySelector('#catalog-items').append(card);}
 }).catch(()=>{status.textContent='Catalog unavailable. Check the local server.';});
 section.querySelector('#build-recipe').onclick=async()=>{
  if(state.busy||!document.getElementById('spec-form').reportValidity())return;
  const spec=readSpec(),button=section.querySelector('#build-recipe'),progress=section.querySelector('#build-progress');
  setBusy(true);progress.hidden=false;section.setAttribute('aria-busy','true');button.textContent='Verifying design…';
  status.textContent=spec.target==='asic'?'Running RTL simulation, generic synthesis, and netlist verification. Larger designs can take a minute.':'Running RTL simulation and checking every output against the integer reference.';
  try{
   const result=await api('/api/build',{spec});
   renderResult(result);if(result.synthesis)renderSynthesis(result.synthesis);
   status.textContent='Verified '+result.build_recipe.block_id+' · '+result.cycles+' simulated cycles'+(result.synthesis?' · '+result.synthesis.cell_count+' generic cells':'')+'. Export the report below for the complete evidence bundle. Physical deployment remains pending.';
   try{await history();}catch(_){status.textContent+=' History refresh failed; the verified report is still available.';}
  }catch(error){status.textContent='Build not accepted: '+error.message;}
  finally{setBusy(false);progress.hidden=true;section.setAttribute('aria-busy','false');button.textContent='Build verified design →';}
 };
 section.querySelector('#export-recipe').onclick=async()=>{
  if(!document.getElementById('spec-form').reportValidity())return;
  const button=section.querySelector('#export-recipe');button.disabled=true;
  try{const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({spec:readSpec()})});const recipe=await response.json();if(!response.ok)throw Error(recipe.error||'Recipe failed');const url=URL.createObjectURL(new Blob([JSON.stringify(recipe,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='siliconos-build-recipe.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Exported '+recipe.block_id+' with exact source hashes. This is a build plan, not a new measurement.';}catch(error){status.textContent=error.message;}finally{button.disabled=false;}
 };
})();
