# Latest reviewed state

Pack assembled November 15, 2026. This is a compilation of existing reviewed evidence, not a fresh app/hardware acceptance or score. Later product work must be checked separately.

## Product and technical evidence

SiliconeOS is the accepted product name; FabZero is the workspace/repository lineage. Accepted slice: signed INT8 matrix inputs and INT32 accumulation; N=8/16 with one/four lanes in software, physical N=8 on KV260. CatalogRTL is the board reference. Other edge-AI workloads, numerical formats, boards, sensors and fleets remain future proposals.

Later clean-room and round 004 evidence supersedes old statements that all board execution/rebuilding/signed import were pending. The reviewed manual app→handoffZIP→KV260→signed import→separate app child loop completed. Both configurations matched all 64 sample outputs with 512/128 reported counters; source/build/report/input/result checks passed, as did seven isolated signing/import tests. Newer one-click orchestration was still unverified on the board at that review; no newer status is asserted here.

Accelerator plus AXI wrapper:354/3,612 LUTs and318/2,470 FFs, zero DSP/BRAM. Four lanes cost about 10.2 times LUTs for one-quarter reported compute clocks, not fourfold end-to-end speedup. Power remains vectorless estimated power. Selected result records/manifests/summaries are included; full bitstreams, XSA, runtime and Vivado build directories are not.

## Customers, market and pricing

Latest company study:14 research candidates,59 source URLs, checked November 15. No outside target-user trial, company buying interest, paid engagement or measured savings was established. Public FPGA use/hiring does not validate demand. Existing vendor/open-source automation is real competition; hardware forecasts are not software TAM. No standalone prompt-to-FPGA software market estimate was established.

US$250 assisted evaluation and future US$149/engineer/month with US$30 provider-cost allowance remain unvalidated/unaccepted proposals. US$19.20 API and US$43.67 direct monthly cost are illustrative unmeasured scenarios, not typical observed usage or net profit.

## Scores and presentation

Latest full review: 59.7/100, independent scores 58/61/60; mean rows: 19/25 execution, 12.7/25 problem/user, 12/20 customer path, 8.7/15 pitch/demo, 7.3/15 creative AI. Earlier full reviews: 28 then 46.3; customer path 12/20 and focused round 00327/45 have different denominators. The market study and packaging issued no new score.

Founder experience helps the story but is not independent demand evidence. Friend feedback, actual qualified-user use, final reviewed presentation and shown consequential AI behavior remained gaps. Recorded demonstrations were the founder's route; the inspected guide expected live working hardware. No exception or automatic disqualification was established.
