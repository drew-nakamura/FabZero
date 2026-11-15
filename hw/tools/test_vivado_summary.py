"""Focused checks for vivado_summary.py using trimmed Vivado 2025.2 report excerpts.

Run: python -m unittest hw/tools/test_vivado_summary.py -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vivado_summary as vs  # noqa: E402

HDR = """| Tool Version : Vivado v.2025.2 (win64) Build 6299465 Fri Nov 14 19:35:11 GMT 2025
| Command      : {cmd}
| Design       : top
| Device       : {dev}
| Design State : {state}
"""

UTIL = HDR + """
1. CLB Logic
------------

+----------------------------+------+-------+------------+-----------+-------+
|          Site Type         | Used | Fixed | Prohibited | Available | Util% |
+----------------------------+------+-------+------------+-----------+-------+
| CLB LUTs*                  | 1541 |     0 |          0 |    117120 |  1.32 |
|   LUT as Distributed RAM   |   40 |     0 |            |           |       |
| CLB Registers              | 2450 |     0 |          0 |    234240 |  1.05 |
+----------------------------+------+-------+------------+-----------+-------+

+-----------+------+-------+------------+-----------+-------+
| Site Type | Used | Fixed | Prohibited | Available | Util% |
+-----------+------+-------+------------+-----------+-------+
| DSPs      |    3 |     0 |          0 |      1248 |  0.24 |
+-----------+------+-------+------------+-----------+-------+
"""

HIER = HDR + """
+----------------+------------+------------+------------+---------+------+------+--------+--------+------+------------+
|    Instance    |   Module   | Total LUTs | Logic LUTs | LUTRAMs | SRLs |  FFs | RAMB36 | RAMB18 | URAM | DSP Blocks |
+----------------+------------+------------+------------+---------+------+------+--------+--------+------+------------+
| top            |      (top) |       1541 |       1455 |      40 |   46 | 2450 |      0 |      0 |    0 |          3 |
|   u_bd         |   bd_wrap  |       1539 |       1453 |      40 |   46 | 2386 |      0 |      0 |    0 |          0 |
|   u_mm         |     matmul |        200 |        150 |      50 |    0 |  300 |      0 |      1 |    0 |          3 |
+----------------+------------+------------+------------+---------+------+------+--------+--------+------+------------+
"""

TIMING = HDR + """
------------------------------------------------------------------------------------------------
| Design Timing Summary
| ---------------------
------------------------------------------------------------------------------------------------

    WNS(ns)      TNS(ns)  TNS Failing Endpoints  TNS Total Endpoints      WHS(ns)      THS(ns)  THS Failing Endpoints  THS Total Endpoints     WPWS(ns)     TPWS(ns)  TPWS Failing Endpoints  TPWS Total Endpoints
    -------      -------  ---------------------  -------------------      -------      -------  ---------------------  -------------------     --------     --------  ----------------------  --------------------
     -0.250       -1.500                      7                 5771        0.018        0.000                      0                 5771        3.500        0.000                       0                  2573


Timing constraints are not met.


------------------------------------------------------------------------------------------------
| Clock Summary
| -------------
------------------------------------------------------------------------------------------------

Clock     Waveform(ns)       Period(ns)      Frequency(MHz)
-----     ------------       ----------      --------------
clk_pl_0  {0.000 5.000}      10.000          100.000


------------------------------------------------------------------------------------------------
| Intra Clock Table
| -----------------
------------------------------------------------------------------------------------------------

Clock             WNS(ns)      TNS(ns)  TNS Failing Endpoints  TNS Total Endpoints      WHS(ns)      THS(ns)
-----             -------      -------  ---------------------  -------------------      -------      -------
clk_pl_0           -0.250       -1.500                      7                 5771        0.018        0.000


Slack (VIOLATED) :        -0.250ns  (required time - arrival time)
  Source:                 u_mm/acc_reg[3]/C
  Destination:            u_mm/acc_reg[31]/D
  Path Group:             clk_pl_0
  Path Type:              Setup (Max at Slow Process Corner)
  Data Path Delay:        9.900ns  (logic 3.000ns (30%)  route 6.900ns (70%))
  Logic Levels:           12  (CARRY8=4 DSP_ALU=1 LUT6=7)
"""

POWER = HDR + """
+--------------------------+--------------+
| Total On-Chip Power (W)  | 2.723        |
| Dynamic (W)              | 2.422        |
| Device Static (W)        | 0.300        |
| Junction Temperature (C) | 31.3         |
| Confidence Level         | Medium       |
+--------------------------+--------------+

+--------------------------+-----------+----------+-----------+-----------------+
| On-Chip                  | Power (W) | Used     | Available | Utilization (%) |
+--------------------------+-----------+----------+-----------+-----------------+
| Clocks                   |     0.005 |        4 |       --- |             --- |
|   LUT as Logic           |     0.001 |     1455 |    117120 |            1.24 |
| PS8                      |     2.415 |        1 |       --- |             --- |
+--------------------------+-----------+----------+-----------+-----------------+

+--------------+-----------+
| Name         | Power (W) |
+--------------+-----------+
| top          |     2.422 |
|   u_bd       |     2.415 |
|   u_mm       |     0.004 |
+--------------+-----------+
"""

DRC = HDR + """
+-----------+------------------+-------------------------+--------+
| Rule      | Severity         | Description             | Checks |
+-----------+------------------+-------------------------+--------+
| PDCN-1569 | Warning          | LUT equation term check | 3      |
| TIMING-1  | Critical Warning | Invalid clock waveform  | 1      |
+-----------+------------------+-------------------------+--------+
"""

SYNTH_LOG = """Start RTL Component Statistics
Detailed RTL Component Info :
+---Adders :
\t   2 Input   32 Bit       Adders := 4
+---Multipliers :
\t   8x8  Multipliers := 1
Finished RTL Component Statistics
Report Cell Usage:
+------+--------+------+
|      |Cell    |Count |
+------+--------+------+
|1     |DSP48E2 |     3|
|2     |LUT6    |   120|
+------+--------+------+
Synthesis finished with 0 errors, 1 critical warnings and 5 warnings.
"""

META = """evidence=out_of_context_synthesis
top=matmul_axi
part=xck26-sfvc784-2LV-c
N=8
LANES=1
requested_period_ns=10
Post-synthesis estimates only.
"""


def fill(template, cmd, dev, state):
    return template.replace("{cmd}", cmd).replace("{dev}", dev).replace("{state}", state)


def write_dir(root, state="Routed", meta=True):
    d = Path(root)
    files = {
        "a.rpt": fill(UTIL, cmd="report_utilization -file a.rpt", dev="xck26-sfvc784-2LV-c", state=state),
        "b.rpt": fill(HIER, cmd="report_utilization -hierarchical -file b.rpt", dev="xck26-sfvc784-2LV-c", state=state),
        "c.rpt": fill(TIMING, cmd="report_timing_summary -file c.rpt", dev="xck26-sfvc784-2LV-c", state=state),
        "d.rpt": fill(POWER, cmd="report_power -file d.rpt", dev="xck26-sfvc784", state=state),
        "e.rpt": fill(DRC, cmd="report_drc -file e.rpt", dev="xck26-sfvc784-2LV-c", state=state),
        "vivado.log": SYNTH_LOG,
    }
    if meta:
        files["build_metadata.txt"] = META
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8")
    return d


class SummaryTests(unittest.TestCase):
    def summarize(self, **kw):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = write_dir(tmp.name, **{k: v for k, v in kw.items() if k in ("state", "meta")})
        return vs.summarize_dir(d, [], kw.get("kernel"), kw.get("cycles"), "simulation", None, None)

    def test_kernel_area_power_and_timing(self):
        s = self.summarize(kernel="u_mm", cycles=512)
        self.assertEqual(s["area"]["Total LUTs"], 200)
        self.assertEqual(s["area"]["LUTRAMs"], 50)
        self.assertEqual(s["area"]["DSP Blocks"], 3)
        self.assertEqual(s["area"]["RAMB18"], 1)
        self.assertEqual(s["power"]["total_w"], 2.723)
        self.assertEqual(s["power"]["kernel_w"], 0.004)
        t = s["timing"]
        self.assertIs(t["constraints_met"], False)
        self.assertEqual(t["WNS"], -0.25)
        self.assertEqual(t["TNS_failing"], 7)
        self.assertEqual(t["clocks"][0]["freq_mhz"], 100.0)
        self.assertEqual(t["fmax_estimates"][0]["estimated_fmax_mhz"], 97.6)  # 1000 / 10.25
        self.assertEqual(t["worst_setup_paths"][0]["logic_levels"], 12)

    def test_ooc_stage_and_matmul_performance(self):
        s = self.summarize(kernel="u_mm", cycles=512)
        self.assertTrue(s["stage"].startswith("Out-of-context synthesis"))
        self.assertEqual((s["N"], s["LANES"]), (8, 1))
        p = s["performance"]
        self.assertEqual(p["macs"], 512)
        self.assertEqual(p["macs_per_cycle"], 1.0)
        self.assertEqual(p["kernel_time_us"], 5.12)
        self.assertEqual(p["gmac_per_s_at_constrained_clock"], 0.1)

    def test_stage_from_design_state_without_metadata(self):
        s = self.summarize(meta=False, state="Synthesized")
        self.assertEqual(s["stage"], "Post-synthesis estimate")
        self.assertEqual(s["area"]["Total LUTs"], 1541)  # whole design when no kernel given
        self.assertEqual(s["performance"], {})

    def test_speed_grade_difference_is_not_a_conflict(self):
        s = self.summarize(kernel="u_mm")
        self.assertFalse([w for w in s["warnings"] if "disagree" in w])

    def test_missing_kernel_is_reported(self):
        s = self.summarize(kernel="u_nope")
        self.assertTrue(any("u_nope" in w for w in s["warnings"]))
        self.assertEqual(s["area"], {})

    def test_drc_and_synthesis_log(self):
        s = self.summarize()
        self.assertEqual(s["checks"]["drc"]["by_severity"], {"Warning": 3, "Critical Warning": 1})
        sy = s["synthesis"]
        self.assertEqual(sy["critical_warnings"], 1)
        self.assertIn({"category": "Multipliers", "item": "8x8 Multipliers", "count": 1},
                      sy["rtl_components"])
        self.assertEqual(sy["cell_usage"]["DSP48E2"], 3)

    def test_cli_writes_markdown_and_json_comparison(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, \
                tempfile.TemporaryDirectory() as out:
            write_dir(a)
            write_dir(b)
            rc = vs.main([a, b, "--kernel", "u_mm", "--cycles", "512", "--cycles", "128",
                          "--label", "1 lane", "--label", "4 lanes", "--out", out])
            self.assertEqual(rc, 0)
            md = (Path(out) / "summary.md").read_text(encoding="utf-8")
            self.assertIn("| Metric | 1 lane | 4 lanes |", md)
            self.assertIn("| Timing met | NO | NO |", md)
            data = json.loads((Path(out) / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual([x["performance"]["cycles"] for x in data["summaries"]], [512, 128])


if __name__ == "__main__":
    unittest.main()
