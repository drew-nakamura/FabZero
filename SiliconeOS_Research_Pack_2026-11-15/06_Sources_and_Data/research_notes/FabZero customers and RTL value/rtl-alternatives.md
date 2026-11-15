# RTL and simpler alternatives

Research accessed November 14, 2026 (America/Los_Angeles). Condensed from the read-only technical researcher; findings use official primary documentation. Proposed applications are inferences.

## Direct counterexample to the label checker

Arduino's Nicla Vision tutorial performs color/brightness blob detection in MicroPython, annotates images, and uses red/green indicators; missing assembly pieces are an example application. This closely resembles the proposed package checker. [Arduino blob detection](https://docs.arduino.cc/tutorials/nicla-vision/blob-detection/).

Microchip describes processor and configurable-hardware tradeoffs, including cases favoring processors on cost/power. Do not claim a universal FPGA advantage. [Microchip FPGA introduction](https://developerhelp.microchip.com/xwiki/bin/view/products/fpga/hello-fpga/why-use/).

## What the hardware deliverable establishes

AMD distinguishes RTL behavioral simulation from physical timing and discusses portable behavioral coding versus device-library dependencies. Streaming hardware can accept subsequent data while earlier data is still processing; initiation rate and total latency are different. [RTL simulation](https://docs.amd.com/r/2025.2-English/ug900-vivado-logic-simulation/Behavioral-Simulation-at-the-Register-Transfer-Level), [streaming interfaces](https://docs.amd.com/r/2024.2-English/ug1399-vitis-hls/Modeling-Streaming-Data-Interfaces).

Synopsys describes FPGA prototyping of synthesizable RTL for pre-silicon hardware/software verification. Such a prototype does not establish future ASIC power, area, analog behavior or manufacturing signoff. [FPGA prototyping](https://www.synopsys.com/blogs/chip-design/scalable-performance-for-soc-design.html).

AMD HLS already generates RTL from C/C++ and supports verification and architectural exploration. Interfaces and constraints remain engineering decisions. [HLS benefits](https://docs.amd.com/r/2025.2-English/ug1399-vitis-hls/Benefits-of-High-Level-Synthesis).

## Inference and limits

Investigate sustained stream acceptance, bounded interface-to-interface latency, concurrent channels, custom protocol/timing, or reusable digital IP. MCU timers/DMA and specialized peripherals also satisfy some such needs. A small function is legitimate when its hardware contract matters. Proposed demos: a streaming image-region processor with real pixel work, or a multichannel event timestamp/trigger block with reproducible event sources. No FPS, speedup, MCU inadequacy, external sensor operation or current KV260 success has been established.
