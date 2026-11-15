# Customer evidence for programmable hardware

Research accessed November 14, 2026 (America/Los_Angeles). Condensed from the read-only customer researcher. Sources are primary vendor/customer publications, not independent benchmarks or evidence of demand for this product.

## Concrete jobs

- Sagemcom engineers describe synchronized parallel acquisition and a 10 microsecond triggered measurement window in an industrial test cell. This is a requirement-based FPGA rationale; their wider production improvements cannot all be attributed to the FPGA. [NI/Sagemcom case study](https://www.ni.com/en/solutions/energy/case-studies/automation-of-a-robotized-production-cell-through-compactrio.html).
- Infineon describes FPGA-based testing of microcontroller peripherals and configurable pulse/protocol behavior. It illustrates demand for flexible digital test interfaces and uses LabVIEW FPGA rather than requiring handwritten RTL. [NI/Infineon case study](https://www.ni.com/en/solutions/semiconductor/case-studies/creating-an-automated-microcontroller-test-system-using-labview-and-fpga.html).
- AMD/Axiomtek describes a K26-based vision product selected for responsive embedded vision. Supplier-published evidence establishes a relevant use category, not transferable KV260 performance. [Axiomtek case study](https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/axiomtek-case-study.pdf).

## Imaging evidence and counterevidence

Basler describes FPGA preprocessing near image acquisition, including filtering/feature extraction, while retaining CPU/GPU roles. It also proposes Python-based FPGA authoring, showing accessible hardware development is an existing direction. [Preprocessing](https://www.baslerweb.com/en-us/capabilities/fpga-based-vision-solution/), [Python initiative](https://www.baslerweb.com/en-us/innovation/fpga-programming-python/).

AMD/Advantech describes optical inspection using CPU/GPU computation. Camera inspection therefore does not establish FPGA necessity. [Advantech case study](https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/aoi-advantech-case-study.pdf).

## Inference and limits

A small technical hardware team with a specified timing, interface or reusable-IP need is a stronger initial hypothesis than any company wanting a camera application. The user could be an embedded engineer; a CTO/founder could approve spending. None of these sources verifies willingness to pay, price, switching behavior or demand for FabZero/SiliconeOS. No outreach occurred. The camera demonstration must show an actual hardware function; occasional crops prove functional execution, not continuous sensor-rate throughput.
