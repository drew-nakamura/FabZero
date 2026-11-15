import { H1, H2, Text, Stack, Table, Link, CollapsibleSection } from "cursor/canvas";

type Company = {
 name: string; group: string; role: string; priority: string; evidence: string;
 sources: [string,string][]; operator: string; buyer: string; trigger: string;
 gap: string; alternative: string; question: string; contact: [string,string]; dates: string;
};
const companies: Company[] = [
  {
    "name": "Leopard Imaging",
    "group": "Product companies",
    "role": "Potential future user / imaging partner",
    "priority": "First interviews",
    "evidence": "Its AUTOMATE 2026 announcement describes ASTRO stereo cameras with two 5.1 MP RGB-IR sensors, FPGA processing and 10GigE for AI perception, navigation and reconstruction. A separate 25 MP demonstration combines FPGA processing with Jetson Thor. Its AMD camera interface supports ZCU102/ZCU104. This is hybrid FPGA preprocessing plus AI compute, not proof all inference is in programmable logic.",
    "sources": [
      [
        "2026 AI-perception announcement",
        "https://leopardimaging.com/leopard-imaging-to-showcase-advanced-ai-perception-and-vision-solutions-at-automate-2026/"
      ],
      [
        "AMD-platform camera interface",
        "https://leopardimaging.com/product/platform-partners/amd/li-multi-sensor-cphy-fmc-101h/"
      ]
    ],
    "operator": "FPGA/embedded-imaging engineer",
    "buyer": "Imaging or embedded engineering lead",
    "trigger": "A sensor, synchronization, buffering or preprocessing change requiring a reproducible lab experiment.",
    "gap": "MIPI/FMC, video streams, clock-domain crossing, DMA, external memory and real image kernels; none is established by the present small GEMM.",
    "alternative": "Sophisticated internal integration and NVIDIA-based platforms; product configuration may matter more than new RTL.",
    "question": "Which repeated FPGA/sensor variation requires the most manual reconstruction of tests, constraints and deployment evidence?",
    "contact": [
      "Official inquiry page",
      "https://leopardimaging.com/contact-us/"
    ],
    "dates": "2026 announcement; other product page undated; checked 2026-11-15."
  },
  {
    "name": "Basler",
    "group": "Product companies",
    "role": "Expert / collaborator / competing framework",
    "priority": "First interviews",
    "evidence": "Basler publicly describes an innovation-stage Python framework for programming FPGAs in cameras/frame grabbers, with image functions and simulation. It explicitly invites feedback on applications, Python and low-code approaches. Its engineering article discusses multi-camera timing, buffers, unsupported formats and insufficient FPGA expertise. This is explicit workflow relevance and evidence of an existing competing approach.",
    "sources": [
      [
        "Python-to-FPGA innovation project",
        "https://www.baslerweb.com/en-us/innovation/fpga-programming-python/"
      ],
      [
        "AI vision engineering constraints",
        "https://www.baslerweb.com/en-us/learning/computing-power-ai-vision-systems/"
      ]
    ],
    "operator": "Applications engineer / FPGA framework engineer",
    "buyer": "Relevant applications or platform engineering lead",
    "trigger": "A customer-specific preprocessing function that must be simulated and deployed on a supported camera/frame grabber.",
    "gap": "Basler targets, interfaces, stream-processing functions, existing framework integration and acceptance tests.",
    "alternative": "Basler is already building an abstraction; it is not a greenfield prompt-tool prospect.",
    "question": "Where would reviewed natural-language intent and retained evidence improve your Python-to-FPGA flow, and where would they add risk?",
    "contact": [
      "Innovation project; public invitation and innovation@baslerweb.com",
      "https://www.baslerweb.com/en-us/innovation/fpga-programming-python/"
    ],
    "dates": "Innovation pages undated; 9M report covers Jan–Sep 2026; checked 2026-11-15."
  },
  {
    "name": "Ouster",
    "group": "Product companies",
    "role": "Potential future engineering user",
    "priority": "First interviews",
    "evidence": "A company-hosted FPGA Design Engineer role explicitly names RTL, verification, testbenches, synthesis, timing closure and lidar integration, with Verilog/SystemVerilog, Vivado or Quartus, FPGA SoCs, AXI and Git. HLS/Vitis and Python/Tcl/Bash are additional skills. Its current platform spans lidar, cameras, compute and software. The job verifies the workflow, not tool-buying interest.",
    "sources": [
      [
        "Official FPGA engineering role",
        "https://ouster.applytojob.com/apply/PvWk0ZFwbL/FPGA-Design-Engineer"
      ],
      [
        "Q3 company release filed with SEC",
        "https://www.sec.gov/Archives/edgar/data/1816581/000162828026069487/exhibit991-9302026.htm"
      ]
    ],
    "operator": "Firmware/FPGA engineer",
    "buyer": "Firmware or hardware engineering leadership",
    "trigger": "A deterministic lidar-data preprocessing/interface variant requiring independently checked outputs and exact build identity.",
    "gap": "Lidar interfaces, calibration, throughput/latency contracts, reliability, enterprise source handling and proprietary RTL.",
    "alternative": "An expert team and mature stack create a high trust/integration bar; the job is not evidence of replacing engineers.",
    "question": "Which repeated RTL-to-lab validation step is painful enough for a third-party tool, and what evidence would your team require?",
    "contact": [
      "Official company contact",
      "https://ouster.com/company/contact-us"
    ],
    "dates": "Job publication date not shown; release Nov 3,2026 for quarter ended Sep 30; checked 2026-11-15."
  },
  {
    "name": "Xnext",
    "group": "Product companies",
    "role": "Later industrial acquisition-workflow candidate",
    "priority": "Later qualification",
    "evidence": "AMD’s 2023 XSpectra case describes Zynq real-time sensor acquisition/firmware in an X-ray inspection system combining sensing and AI/CNN software. Xnext’s current site still presents AI/deep-learning hyperspectral contaminant inspection. The case does not establish that the CNN runs in FPGA fabric.",
    "sources": [
      [
        "2023 vendor/customer case",
        "https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/xnext-pbx.pdf"
      ],
      [
        "Current company product site",
        "https://www.x-next.com/"
      ]
    ],
    "operator": "FPGA/embedded acquisition engineer",
    "buyer": "R&D or embedded systems lead",
    "trigger": "A detector acquisition, filter or buffer change with a known test input and reference output.",
    "gap": "Detector interfaces, streaming, acquisition semantics, quality/latency constraints and production qualification.",
    "alternative": "Existing custom electronics, firmware and trained inspection software; small GEMM is far from complete inspection.",
    "question": "When acquisition/preprocessing firmware changes, how do you validate and preserve the detector-to-result evidence across variants?",
    "contact": [
      "Official site / info@x-next.com",
      "https://www.x-next.com/"
    ],
    "dates": "FPGA evidence2023; current site checked2026-11-15."
  },
  {
    "name": "SICK",
    "group": "Product companies",
    "role": "Later enterprise user / expert benchmark",
    "priority": "Later qualification",
    "evidence": "AMD’s 2024 case documents Kintex UltraScale+, FINN and deep-learning processing in Lector/Inspector machine vision, including capture, compression and pre-segmentation. A 2025 case documents Zynq UltraScale+ in picoScan lidar for mobile robots. Performance claims in the first case were supplied by SICK and not independently verified by AMD.",
    "sources": [
      [
        "2024 machine-vision case",
        "https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/sick-case-study.pdf"
      ],
      [
        "2025 lidar case",
        "https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/sick-2d-lidar.pdf"
      ]
    ],
    "operator": "Embedded FPGA / accelerator engineer",
    "buyer": "Platform or R&D engineering manager",
    "trigger": "A supported preprocessing/quantized-network block revision within an existing qualified toolchain.",
    "gap": "FINN/network/streaming integration, exact sensor targets and quality/latency qualification.",
    "alternative": "Substantial existing platform and open-source FPGA ML compiler; strong use evidence is not an easy first sale.",
    "question": "What repeated experiment remains inconvenient after FINN and your current tools, and would an external orchestrator preserve qualification?",
    "contact": [
      "Official US contact / info@sick.com",
      "https://www.sick.com/us/en/contact/w/contactflyout_general_contacts"
    ],
    "dates": "FPGA cases2024/2025; FY2025 figures; checked2026-11-15."
  },
  {
    "name": "IDS Imaging",
    "group": "Product companies",
    "role": "Model-specific user hypothesis",
    "priority": "Requalify architecture",
    "evidence": "IDS describes its deep ocean FPGA core for NXT cameras. Its component material distinguishes rio/rome deep ocean from malibu’s Ambarella accelerator; newer malibu/oslo material explicitly describes an Ambarella SoC/NPU. The entire IDS edge-AI camera family cannot be counted as FPGA hardware.",
    "sources": [
      [
        "FPGA technical article",
        "https://en.ids-imaging.com/technical-articles-details/items/ids-nxt-ai-for-all.html?label=53"
      ],
      [
        "System component distinction",
        "https://www.ids-imaging.us/ids-nxt-system-components.html"
      ],
      [
        "Current malibu/oslo NPU products",
        "https://en.ids-imaging.com/ids-nxt-malibu-oslo.html"
      ]
    ],
    "operator": "Engineer for the actual programmable-fabric camera family",
    "buyer": "Relevant camera-platform engineering lead",
    "trigger": "An active FPGA-camera core/preprocessing update, if that product family remains relevant.",
    "gap": "Proprietary core/toolchain, camera I/O, network support and production evaluation.",
    "alternative": "Existing training/app deployment tools; newer NPU products may remove custom FPGA work.",
    "question": "Which active products still use programmable fabric, and where does custom RTL remain necessary rather than the NPU/app workflow?",
    "contact": [
      "Official contact",
      "https://www.ids-imaging.us/contact.html"
    ],
    "dates": "Technical pages undated/current family material; company milestone2025; checked2026-11-15."
  },
  {
    "name": "Prophesee",
    "group": "Product companies",
    "role": "Historical KV260 partner / requalification",
    "priority": "Requalify architecture",
    "evidence": "Its May 6,2024 announcement and AMD case document Metavision event-based sensing/AI with Kria KV260. However, its official product page says the kit was discontinued Aug 31,2026 and is no longer available. Historical same-board fit is not a current purchasable product/channel.",
    "sources": [
      [
        "Official kit and discontinued status",
        "https://www.prophesee.ai/event-based-metavision-amd-kria-starter-kit/"
      ],
      [
        "AMD customer case",
        "https://www.amd.com/en/resources/case-studies/prophesee.html"
      ]
    ],
    "operator": "Event-stream FPGA / embedded engineer, if current architecture uses fabric",
    "buyer": "Current evaluation/platform engineering lead",
    "trigger": "A present event-stream processing experiment only after confirming the new architecture.",
    "gap": "Current platform, event sensor/SDK and real stream processing; discontinued KV260 kit cannot establish compatibility.",
    "alternative": "Existing SDK/reference apps and a shift to more integrated systems may remove the close fit.",
    "question": "After discontinuing the KV260 kit, where does programmable logic remain in the current evaluation/product flow?",
    "contact": [
      "Official contact",
      "https://www.prophesee.ai/contact-us/"
    ],
    "dates": "Original2024 collaboration; discontinued2026-08-31; company facts checked2026-11-15."
  },
  {
    "name": "LogicTronix",
    "group": "Workflow specialists",
    "role": "Expert evaluator / potential future user or partner",
    "priority": "First interviews",
    "evidence": "It identifies as an AMD-Xilinx design-services and Kria SoM AI/ML design partner. Public services explicitly include KV260/VVAS, multi-channel/multi-model inference, RTL, embedded Linux and carrier work. Its IP portfolio confirms FPGA solution work.",
    "sources": [
      [
        "Services and inquiry",
        "https://logictronix.com/fpga-design-services/"
      ],
      [
        "FPGA IP portfolio",
        "https://logictronix.com/solutions-ip-cores/logictronix-fpga-ip-cores/"
      ]
    ],
    "operator": "Senior FPGA / ML engineer",
    "buyer": "Engineering lead or customer-project owner",
    "trigger": "A customer-specific Kria configuration requiring repeatable PL/model/implementation/deployment checks.",
    "gap": "Real VVAS/Vitis-AI, model integration, memory/stream interfaces, Linux packaging and customer IP handling.",
    "alternative": "It already sells the integration work and likely has tooling; partnership/competition may be more realistic than seat sales.",
    "question": "For the last KV260 customer variation, what changed and was rechecked between the model, PL integration, implementation and deployment?",
    "contact": [
      "Official services inquiry form",
      "https://logictronix.com/fpga-design-services/"
    ],
    "dates": "Pages undated; checked2026-11-15."
  },
  {
    "name": "Starware Design",
    "group": "Workflow specialists",
    "role": "Expert evaluator / small-firm user hypothesis",
    "priority": "First interviews",
    "evidence": "Current services cover FPGA/ASIC verification, board bring-up, embedded software and edge AI. Its DevOps article describes source/bitstream mismatch, unreproducible environments and dependence on one release engineer. The article lists admin and no clear date; current site material also describes GitLab CI/Vivado/Cocotb work.",
    "sources": [
      [
        "Company services",
        "https://www.starwaredesign.com/"
      ],
      [
        "First-person FPGA DevOps account",
        "https://www.starwaredesign.com/fpga-meets-devops-introduction/"
      ]
    ],
    "operator": "FPGA project lead / principal consultant",
    "buyer": "Founder/principal or project owner",
    "trigger": "A customer handoff requiring proof that source, build and physical result belong together.",
    "gap": "Existing CI integration, customer-owned designs, reproducible environments and actual project checks.",
    "alternative": "It already knows and uses CI; an earlier pain account does not prove the problem is still unsolved.",
    "question": "Which part of a recent source-to-tested-board handoff still required reconstruction after your existing CI work?",
    "contact": [
      "Official Get in touch route; contact page timed out in this pass",
      "https://www.starwaredesign.com/"
    ],
    "dates": "DevOps article undated; current site checked2026-11-15."
  },
  {
    "name": "hema electronic",
    "group": "Workflow specialists",
    "role": "Platform / qualification partner hypothesis",
    "priority": "Platform partners",
    "evidence": "The German electronics firm’s AMD-coordinated platform supplements K26/KV260 development. KV260 and EVB2 both use K26; EVB2 is positioned for customizable embedded vision/sensor/AI work toward production. Shared silicon does not make bitstreams interchangeable.",
    "sources": [
      [
        "AMD FPGA platform",
        "https://www.hema.de/loesungen/amd-fpga-plattform"
      ],
      [
        "Official contact",
        "https://www.hema.de/unternehmen/kontakt"
      ]
    ],
    "operator": "Platform FPGA / embedded-vision engineer",
    "buyer": "Platform engineering or business-development lead",
    "trigger": "Moving a feasibility variant from KV260 to EVB2/custom carrier with transferrable acceptance evidence.",
    "gap": "Carrier constraints, sensors/interfaces, clocks/drivers and production validation.",
    "alternative": "Platform reuse already addresses part of development effort; no numerical saving established.",
    "question": "What configuration and validation steps repeat between KV260 feasibility work and an EVB2/custom carrier?",
    "contact": [
      "Official sales/contact",
      "https://www.hema.de/unternehmen/kontakt"
    ],
    "dates": "Pages undated; checked2026-11-15."
  },
  {
    "name": "Enclustra",
    "group": "Workflow specialists",
    "role": "Platform partner / established orchestration competitor",
    "priority": "Platform partners",
    "evidence": "Services include specifications, HDL, verification, software and prototyping for edge AI. Its Sep 21,2026 announcement pairs MakarenaLabs MuseBox, branded Lira, with its portfolio for hardware-accelerated local edge-AI pipelines. Its wider SoC/MPSoC/MLSoC portfolio is not all FPGA.",
    "sources": [
      [
        "Design services",
        "https://www.enclustra.com/en/design-services/"
      ],
      [
        "Lira orchestration partnership",
        "https://www.enclustra.com/en/company/news-events/news/enclustra-partner-with-makarenalabs-on-edge-ai-orchestration/"
      ]
    ],
    "operator": "FPGA platform architect / services engineer",
    "buyer": "Design-services or platform lead",
    "trigger": "An experiment/evidence gap complementary to existing Lira orchestration.",
    "gap": "Actual module/tool recipes and a demonstrably complementary function.",
    "alternative": "An existing orchestration partner directly weakens a generic one-workflow sales pitch.",
    "question": "What remains manual in custom RTL verification and physical acceptance after Lira and your design-services tooling?",
    "contact": [
      "Official design-services route",
      "https://www.enclustra.com/en/design-services/"
    ],
    "dates": "Partnership2026-09-21; services checked2026-11-15."
  },
  {
    "name": "Missing Link Electronics",
    "group": "Workflow specialists",
    "role": "Automation competitor / interoperability partner",
    "priority": "Competitive benchmarks",
    "evidence": "MLE lists reduced-precision neural networks, vision, RTL/HLS, AXI, timing closure and automated builds. Its company-owned FPGA-vbs automates Vivado variants, reports and Git/dirty-state identity.",
    "sources": [
      [
        "Competencies",
        "https://www.missinglinkelectronics.com/design-services/competence-areas/"
      ],
      [
        "fpga-vbs source",
        "https://github.com/missinglinkelectronics/fpga-vbs"
      ]
    ],
    "operator": "FPGA tooling / design-services engineer",
    "buyer": "Tooling or services lead",
    "trigger": "An acceptance/physical-result step outside the existing variant-build system.",
    "gap": "Interoperability with its subsystems, streaming/data-movement interfaces and CI.",
    "alternative": "Already provides substantial automation; no evidence it wants a paid prompt wrapper.",
    "question": "Which physical acceptance/handoff step remains outside FPGA-vbs, and would reviewed specifications improve it?",
    "contact": [
      "Official technical inquiry",
      "https://www.missinglinkelectronics.com/contact/"
    ],
    "dates": "Current pages/repository checked2026-11-15."
  },
  {
    "name": "Antmicro",
    "group": "Workflow specialists",
    "role": "Open-source tooling competitor / collaboration candidate",
    "priority": "Competitive benchmarks",
    "evidence": "Its FPGA work includes AI accelerators and VEDLIoT. Topwrap connects and parameterizes HDL modules and generates top-level wrappers through CLI/graphical workflows. Announcement Aug 19,2024; documentation updated Sep 1,2026.",
    "sources": [
      [
        "FPGA technology work",
        "https://antmicro.com/technologies/fpga/"
      ],
      [
        "Topwrap announcement",
        "https://antmicro.com/blog/2024/08/parameterizable-digital-logic-design-with-the-topwrap-toolkit/"
      ],
      [
        "Topwrap documentation",
        "https://antmicro.github.io/topwrap/"
      ]
    ],
    "operator": "FPGA tooling / project engineer",
    "buyer": "Tooling or project lead",
    "trigger": "A real experiment still hard after Topwrap and current simulation/CI.",
    "gap": "Open-interface interoperability, co-simulation and broader IP validation.",
    "alternative": "Already builds integration infrastructure; generic HDL-tool orchestration is insufficient differentiation.",
    "question": "What customer task remains difficult after Topwrap and your simulation/CI stack when physical evidence is required?",
    "contact": [
      "Official contact / contact@antmicro.com",
      "https://antmicro.com/about/contact/"
    ],
    "dates": "Announcement2024-08-19; docs2026-09-01; checked2026-11-15."
  },
  {
    "name": "TOPIC Embedded Systems",
    "group": "Workflow specialists",
    "role": "T&S platform supplier / legacy automation benchmark",
    "priority": "Competitive benchmarks",
    "evidence": "TOPIC joined Technology & Strategy in March2023. Current Miami platforms include Zynq-7000, Zynq UltraScale+ and Versal. Legacy Dyplo material describes software-to-FPGA deployment, streaming/DMA and partial reconfiguration, but its old product link now redirects to a general portfolio; current standalone Dyplo availability was not verified.",
    "sources": [
      [
        "2023 T&S integration",
        "https://topic.nl/nieuws/integration-of-topic-with-ts-group"
      ],
      [
        "Current platforms",
        "https://topic.nl/products"
      ],
      [
        "Legacy Dyplo route",
        "https://topic.nl/us/dyplo"
      ]
    ],
    "operator": "FPGA platform / services engineer",
    "buyer": "Platform or design-services lead",
    "trigger": "A customer-specific Miami accelerator with unautomated acceptance/evidence steps.",
    "gap": "Actual Miami profiles, Linux/DMA interfaces and project-level acceptance.",
    "alternative": "Existing supplier platform/deployment expertise; legacy Dyplo is not confirmed current paid software.",
    "question": "Which requirements-to-verified-artifact steps remain manual beyond the platform and deployment tools you already provide?",
    "contact": [
      "Current product/contact route; info@topic.nl",
      "https://topic.nl/products"
    ],
    "dates": "T&S integration2023-03-30; current portfolio checked2026-11-15."
  }
];
const markets = [
 {name:"Edge-AI FPGA silicon", base:"2024 estimate · $1.1183bn", end:"2030 forecast · $2.0232bn", growth:"10.4% · 2024–2030", scope:"SHD2025 · global hardware only; 2026forecast $1.3952bn", url:"https://theshdgroup.com/wp-content/uploads/2025/07/Edge-AI-2025-Report-070125-final-1.pdf"},
 {name:"All FPGA hardware", base:"2025 estimate · $11.73bn", end:"2030 forecast · $19.34bn", growth:"10.5% · 2025–2030", scope:"MarketsandMarkets Oct2025 · all applications / FPGA and eFPGA", url:"https://www.marketsandmarkets.com/Market-Reports/fpga-market-194123367.html"},
 {name:"Edge-AI chips/devices", base:"2024 estimate · $32.3775bn", end:"2030 forecast · $102.8901bn", growth:"21.3% · 2024–2030", scope:"SHD2025 · heterogeneous processors, not FPGA-only", url:"https://theshdgroup.com/wp-content/uploads/2025/07/Edge-AI-2025-Report-070125-final-1.pdf"},
 {name:"Edge-AI hardware", base:"2025 estimate · $26.14bn", end:"2030 forecast · $58.90bn", growth:"17.6% · 2025–2030", scope:"MarketsandMarkets · processors/memory/modules", url:"https://www.marketsandmarkets.com/ResearchInsight/edge-ai-hardware-market-size-outlook.asp"},
 {name:"Broad edge-AI ecosystem", base:"2026 estimate · $30.0bn", end:"2033 forecast · $118.7bn", growth:"21.7% · 2026–2033", scope:"GVR · hardware/software/edge cloud/services", url:"https://www.grandviewresearch.com/industry-analysis/edge-ai-market-report"}
];
export default function EdgeAIFPGACustomerMarket() {
 return <Stack gap={20} style={{padding:24}}>
  <Stack gap={8}>
   <H1>Edge AI FPGA customer market</H1>
   <Text weight="medium">Start with engineers already designing FPGA logic. Fourteen researched companies; zero contacted or validated buyers.</Text>
   <Text tone="secondary" size="small">Checked November 15, 2026. Public evidence and forecasts; buyer roles and prioritization are hypotheses. Current SiliconeOS supports a small INT8 KV260 matrix experiment, not the production systems below.</Text>
  </Stack>
  <Stack gap={8}>
   <H2>First interviews: five strong technical routes</H2>
   <Text>LogicTronix and Starware for specialist workflow critique; Leopard Imaging and Ouster for real perception FPGA work; Basler for its explicit FPGA-programming innovation invitation. Basler also builds competing tooling. hema is a possible platform partner.</Text>
  </Stack>
  <Stack gap={8}>
   <H2>Growth is hardware context, not software TAM</H2>
   <Text>The closest segment is FPGA silicon used in edge AI: approximately $1.12bn in 2024 to $2.02bn forecast for 2030. Its 10.4% CAGR is slower than SHD's broad 21.3% chip forecast. Derived FPGA share falls 3.45%→1.97% in that model.</Text>
   <Table headers={["Market definition / source","Base estimate · USD","Forecast · USD","CAGR and window","Coverage"]}
    rows={markets.map(m=>[<Link href={m.url}>{m.name}</Link>,m.base,m.end,m.growth,m.scope])} stickyHeader />
   <Text size="small" tone="secondary">Original publisher summaries checked Nov 15. Different definitions/years/methods: do not add or average rows. SHD Table12, printedp51/PDFindex57, uses USDmillions; report labels differ April/July/March2025. Market studies were not purchased; forecasts are uncertain.</Text>
  </Stack>
  <Stack gap={8}>
   <H2>Reported design-industry spending is a different measure</H2>
   <Table headers={["SEMI/ESD category","Q2 2026 · USD millions","YoY growth"]} rows={[
    ["Electronic system design total", "5,710.8", "+12.2%"],
    ["Computer-Aided Engineering", "2,077.6", "+7.7%"],
    ["IC physical design and verification", "818.3", "+16.6%"],
    ["Semiconductor IP", "2,199.0", "+20.4%"]]} />
   <Text size="small" tone="secondary">Reported quarterly global categories, not annual FPGA software spending. Source: <Link href="https://www.semi.org/en/semi-press-release/electronic-system-design-industry-posts-$5.7-billion-in-revenue-in-q2-2026-esd-alliance-reports">SEMI release, October 19, 2026</Link>.</Text>
  </Stack>
  <Stack gap={8}>
   <H2>Company fit and current product gaps</H2>
   <Table headers={["Company","Research role / priority","Specific task hypothesis","What today's product lacks"]}
    rows={companies.map(c=>[<Link href={c.contact[1]}>{c.name}</Link>,c.role+" · "+c.priority,c.trigger,c.gap])} stickyHeader />
   <Text tone="secondary" size="small">Public contact links are possible discovery routes, not interested prospects. Company revenues, staff, funding and shipped sensors are not eligible software seats or purchasing budgets. Current prototype is a methodology example for these companies, not production-compatible.</Text>
  </Stack>
  <Stack gap={8}>
   <H2>Inspect evidence and ask one specific question</H2>
   {companies.map(c=><CollapsibleSection key={c.name} title={c.name+" — "+c.group}>
    <Stack gap={8}>
     <Text>{c.evidence}</Text>
     <Text size="small" tone="secondary">{c.dates}</Text>
     <Text>Operator hypothesis: {c.operator}. Buyer hypothesis: {c.buyer}.</Text>
     <Text>{c.alternative}</Text>
     <Text weight="medium">{c.question}</Text>
     {c.sources.map(([label,url])=><Link key={url} href={url}>{label}</Link>)}
     <Link href={c.contact[1]}>{c.contact[0]}</Link>
    </Stack>
   </CollapsibleSection>)}
  </Stack>
  <Stack gap={8}>
   <H2>Direct competition already exists</H2>
   <Text><Link href="https://ir.latticesemi.com/news-releases/news-release-details/lattice-advances-fpga-design-new-leadership-ai-driven">Lattice Prompt · September 16, 2026</Link> is advertised as a free assistant download for natural-language Radiant tasks. That does not make LLM/IDE/device/IP operation universally free. Its 10× claim is vendor marketing, not our result.</Text>
   <Text><Link href="https://www.altera.com/newsroom/altera-launches-quartusIQ">Altera QuartusIQ · October 21, 2026</Link> announces contextual natural-language design/debug/timing assistance, with availability scheduled October 28. Its expected 1.5× total-design-cycle gain was not independently benchmarked here.</Text>
   <Text>Topwrap, fpga-vbs, Basler's Python framework and Enclustra/Lira already automate parts of the work. Test incremental value in a supported independently checked experiment, rather than claiming prompt-to-FPGA is new.</Text>
  </Stack>
  <Stack gap={8}>
   <H2>No measured prompt-to-FPGA software TAM was found</H2>
   <Text>Size from qualified companies × eligible engineers × actual adoption × price. At the prior hypothetical $149/month, a continuously paying seat produces $1,788/year before churn/discounts. For illustration only: 100 companies × 5 engineers × 20% adoption gives 100 seats / $178,800 ARR. These are invented scenario inputs, not observed TAM/SAM/SOM.</Text>
   <Text weight="medium">Next evidence: one relevant engineer's recent task, current tools and exact acceptance criteria; observed switching benefit; then an actual budget-owner response. No market growth figure supplies that evidence.</Text>
  </Stack>
 </Stack>;
}
