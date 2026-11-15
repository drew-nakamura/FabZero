#!/usr/bin/env python3
"""Turn Vivado report folders into a short Markdown + JSON summary.

Usage:
  python hw/tools/vivado_summary.py REPORT_DIR [REPORT_DIR ...]
      [--kernel INSTANCE] [--cycles N --cycles-source simulation|board|expected]
      [--n N] [--label NAME ...] [--out DIR]

Each REPORT_DIR may contain any of: Vivado .rpt files (utilization, hierarchical
utilization, timing summary, timing paths, power, DRC, methodology), a Vivado
.log with synthesis output, build_metadata.txt (hardware/synth.tcl) and
design_info.txt (hw/tools/collect_reports.tcl). Reports are recognised by the
"Command" line in their header, not by file name. Extra --log files can be given.

Several folders produce a side-by-side comparison (e.g. LANES=1 vs LANES=4).
Writes summary.md and summary.json to --out (default: the single REPORT_DIR).
Standard library only. The summary restates report contents; it is not
evidence that a bitstream was generated, loaded or executed.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "fabzero.vivado_summary/1"
KEY_RESOURCES = ["CLB LUTs", "LUT as Logic", "LUT as Distributed RAM", "LUT as Shift Register",
                 "CLB Registers", "CARRY8", "Block RAM Tile", "RAMB36/FIFO*", "RAMB18",
                 "URAM", "DSPs", "Bonded IOB"]
HIER_COLUMNS = ["Total LUTs", "Logic LUTs", "LUTRAMs", "SRLs", "FFs", "RAMB36", "RAMB18",
                "URAM", "DSP Blocks"]
SUMMARY_NUMS = ["WNS", "TNS", "TNS_failing", "TNS_endpoints", "WHS", "THS", "THS_failing",
                "THS_endpoints", "WPWS", "TPWS", "TPWS_failing", "TPWS_endpoints"]


# ---------------------------------------------------------------- helpers
def read_text(path):
    raw = Path(path).read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8-sig", errors="replace")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def num(text):
    """Parse a report cell into int/float; keep '<0.01'-style values as strings."""
    if text is None:
        return None
    t = str(text).strip()
    if t in ("", "---", "NA", "-"):
        return None
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        return t


def header_fields(text):
    fields = {}
    for line in text.splitlines()[:40]:
        m = re.match(r"^\|\s*([A-Za-z][A-Za-z ]+?)\s*:\s*(.*?)\s*$", line)
        if m:
            fields[m.group(1)] = m.group(2)
    return fields


def ascii_tables(lines, start=0, stop=None):
    """Yield (first_line_index, header_cells, rows) for '|' tables. Rows keep raw first cell."""
    stop = len(lines) if stop is None else stop
    i = start
    while i < stop:
        if lines[i].startswith("|") or lines[i].startswith("+"):
            j = i
            block = []
            while j < stop and (lines[j].startswith("|") or lines[j].startswith("+")):
                if lines[j].startswith("|"):
                    parts = lines[j].rstrip().split("|")[1:-1]
                    if parts:
                        block.append(parts)
                j += 1
            if block and len(block[0]) >= 2:
                hdr = [c.strip() for c in block[0]]
                yield i, hdr, block[1:]
            i = j
        else:
            i += 1


def indent_of(raw_cell):
    return max(0, (len(raw_cell) - len(raw_cell.lstrip()) - 1) // 2)


def classify(path, text):
    name = path.name.lower()
    if name == "build_metadata.txt":
        return "build_metadata"
    if name == "design_info.txt":
        return "design_info"
    cmd = header_fields(text).get("Command", "")
    if cmd.startswith("report_utilization"):
        return "utilization_hier" if "-hierarchical" in cmd else "utilization"
    for key in ("report_timing_summary", "report_power", "report_drc", "report_methodology"):
        if cmd.startswith(key):
            return key.replace("report_", "")
    if cmd.startswith("report_timing"):
        return "timing_paths"
    if "Start RTL Component Statistics" in text or "Synthesis finished with" in text:
        return "synth_log"
    return None


# ---------------------------------------------------------------- parsers
def parse_kv(text):
    out, notes = {}, []
    for line in text.splitlines():
        if "=" in line and not line.startswith(" "):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
        elif line.strip():
            notes.append(line.strip())
    if notes:
        out["notes"] = notes
    return out


def parse_utilization(text):
    res = {}
    for _, hdr, rows in ascii_tables(text.splitlines()):
        if hdr[0] != "Site Type" or "Used" not in hdr:
            continue
        iu = hdr.index("Used")
        ia = hdr.index("Available") if "Available" in hdr else None
        ip = hdr.index("Util%") if "Util%" in hdr else None
        for r in rows:
            name = r[0].strip().rstrip("*").strip()  # synthesis reports mark estimates as "CLB LUTs*"
            if name and name not in res:
                res[name] = {"used": num(r[iu]),
                             "available": num(r[ia]) if ia is not None and ia < len(r) else None,
                             "util_pct": num(r[ip]) if ip is not None and ip < len(r) else None}
    return res


def parse_utilization_hier(text):
    rows_out = []
    for _, hdr, rows in ascii_tables(text.splitlines()):
        if hdr[0] != "Instance" or "Module" not in hdr:
            continue
        stack = []
        for r in rows:
            depth = indent_of(r[0])
            name = r[0].strip()
            stack = stack[:depth] + [name]
            path = "/".join(stack[1:]) if depth > 0 else ""
            entry = {"instance": name, "path": path, "depth": depth,
                     "module": r[1].strip(), "self_only": name.startswith("(")}
            for col in HIER_COLUMNS:
                if col in hdr and hdr.index(col) < len(r):
                    entry[col] = num(r[hdr.index(col)])
            rows_out.append(entry)
        break
    return rows_out


def parse_paths(text, limit=10):
    paths = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^Slack \((MET|VIOLATED)\)\s*:\s*(-?[\d.]+)ns", line)
        if not m:
            continue
        p = {"status": m.group(1), "slack_ns": float(m.group(2))}
        for nxt in lines[i + 1:i + 40]:
            if nxt.startswith("Slack"):
                break
            for key, label in (("source", "Source:"), ("destination", "Destination:"),
                               ("path_group", "Path Group:"), ("path_type", "Path Type:")):
                if nxt.strip().startswith(label) and key not in p:
                    p[key] = nxt.split(":", 1)[1].strip()
            md = re.search(r"Data Path Delay:\s*([\d.]+)ns", nxt)
            if md:
                p["data_path_delay_ns"] = float(md.group(1))
            ml = re.search(r"Logic Levels:\s*(\d+)\s*(\(.*\))?", nxt)
            if ml:
                p["logic_levels"] = int(ml.group(1))
                if ml.group(2):
                    p["logic_detail"] = ml.group(2).strip("()")
        paths.append(p)
    setup = sorted((p for p in paths if "Max" in p.get("path_type", "Max")),
                   key=lambda p: p["slack_ns"])
    return setup[:limit]


def parse_timing_summary(text):
    lines = text.splitlines()
    out = {"constraints_met": None, "design": {}, "clocks": [], "intra_clock": [],
           "check_timing": {}}
    if "All user specified timing constraints are met." in text:
        out["constraints_met"] = True
    elif re.search(r"Timing constraints are not met", text):
        out["constraints_met"] = False
    for m in re.finditer(r"checking (\w+) \((\d+)\)", text):
        out["check_timing"].setdefault(m.group(1), int(m.group(2)))
    for i, line in enumerate(lines):
        if "Design Timing Summary" in line:
            for j in range(i, min(i + 15, len(lines))):
                vals = lines[j].split()
                if len(vals) == 12 and all(re.match(r"^-?[\d.]+$", v) for v in vals):
                    out["design"] = dict(zip(SUMMARY_NUMS, map(num, vals)))
                    break
            break
    sec = None
    for line in lines:
        if line.startswith("| Clock Summary"):
            sec = "clock"
            continue
        if line.startswith("| Intra Clock Table"):
            sec = "intra"
            continue
        if line.startswith("| ") and sec and not line.startswith("| -"):
            sec = None
            continue
        if sec == "clock":
            m = re.match(r"^\s*(\S+)\s+\{([^}]*)\}\s+([\d.]+)\s+([\d.]+)", line)
            if m:
                out["clocks"].append({"name": m.group(1), "period_ns": float(m.group(3)),
                                      "freq_mhz": float(m.group(4))})
        elif sec == "intra":
            vals = line.split()
            if len(vals) >= 2 and re.match(r"^-?[\d.]+$", vals[1]) and not vals[0].startswith("-"):
                out["intra_clock"].append({"clock": vals[0], "WNS": num(vals[1]),
                                           "WHS": num(vals[5]) if len(vals) > 5 else None})
    out["worst_setup_paths"] = parse_paths(text, limit=5)
    return out


def parse_power(text):
    out = {}
    for key, label in (("total_w", "Total On-Chip Power (W)"), ("dynamic_w", "Dynamic (W)"),
                       ("static_w", "Device Static (W)"), ("junction_c", "Junction Temperature (C)"),
                       ("confidence", "Confidence Level")):
        m = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*([^|]+?)\s*\|", text)
        if m:
            out[key] = num(m.group(1))
    out["components"], out["hierarchy"] = [], []
    for _, hdr, rows in ascii_tables(text.splitlines()):
        if hdr[0] == "On-Chip" and not out["components"]:
            for r in rows:
                out["components"].append({"name": r[0].strip(), "depth": indent_of(r[0]),
                                          "power_w": num(r[1])})
        elif hdr[:2] == ["Name", "Power (W)"] and not out["hierarchy"]:
            stack = []
            for r in rows:
                d = indent_of(r[0])
                stack = stack[:d] + [r[0].strip()]
                out["hierarchy"].append({"path": "/".join(stack[1:]), "depth": d,
                                         "power_w": num(r[1])})
    return out


def parse_rule_table(text):
    rules = []
    for _, hdr, rows in ascii_tables(text.splitlines()):
        if hdr[:2] == ["Rule", "Severity"]:
            for r in rows:
                rules.append({"rule": r[0].strip(), "severity": r[1].strip(),
                              "description": r[2].strip() if len(r) > 2 else "",
                              "checks": num(r[3]) if len(r) > 3 else None})
    counts = {}
    for r in rules:
        counts[r["severity"]] = counts.get(r["severity"], 0) + (r["checks"] or 1)
    return {"rules": rules, "by_severity": counts}


def parse_synth_log(text):
    out = {"rtl_components": [], "mapping_tables": [], "cell_usage": {}}
    m = re.search(r"Synthesis finished with (\d+) errors, (\d+) critical warnings and (\d+) warnings",
                  text)
    if m:
        out["errors"], out["critical_warnings"], out["warnings"] = map(int, m.groups())
    for block in re.findall(r"Detailed RTL Component Info :(.*?)Finished RTL Component Statistics",
                            text, re.S):
        cat = None
        for line in block.splitlines():
            mc = re.match(r"^\+---(.+?)\s*:\s*$", line.strip())
            if mc:
                cat = mc.group(1)
                continue
            mi = re.match(r"^(.*?)\s*:=\s*(\d+)\s*$", line.strip())
            if mi and cat:
                out["rtl_components"].append({"category": cat,
                                              "item": " ".join(mi.group(1).split()),
                                              "count": int(mi.group(2))})
    lines = text.splitlines()
    for i, line in enumerate(lines):
        title = line.strip()
        if re.search(r"(Mapping Report|DSP Final Report|Report Cell Usage)", title):
            for _, hdr, rows in ascii_tables(lines, i + 1, min(i + 200, len(lines))):
                if "Report Cell Usage" in title and hdr[1:3] == ["Cell", "Count"]:
                    for r in rows:
                        out["cell_usage"][r[1].strip()] = num(r[2])
                else:
                    out["mapping_tables"].append({"title": title.strip(": "), "header": hdr,
                                                  "rows": [[c.strip() for c in r] for r in rows]})
                break
    return out


PARSERS = {"utilization": parse_utilization, "utilization_hier": parse_utilization_hier,
           "timing_summary": parse_timing_summary, "timing_paths": parse_paths,
           "power": parse_power, "drc": parse_rule_table, "methodology": parse_rule_table,
           "synth_log": parse_synth_log, "build_metadata": parse_kv, "design_info": parse_kv}


# ---------------------------------------------------------------- summary
def summarize_dir(folder, extra_logs, kernel, cycles, cycles_source, n_override, label):
    folder = Path(folder)
    files = sorted(p for p in folder.iterdir()
                   if p.is_file() and p.suffix.lower() in (".rpt", ".txt", ".log"))
    files += [Path(p) for p in extra_logs]
    s = {"label": label or folder.name, "folder": str(folder.resolve()), "inputs": [],
         "warnings": []}
    parsed_by_kind = {}
    for p in files:
        text = read_text(p)
        kind = classify(p, text)
        if kind is None:
            continue
        hdr = header_fields(text)
        s["inputs"].append({"file": str(p.resolve()), "kind": kind, "sha256": sha256(p),
                            "design_state": hdr.get("Design State"), "tool": hdr.get("Tool Version"),
                            "device": hdr.get("Device"), "design": hdr.get("Design"),
                            "date": hdr.get("Date")})
        if kind in parsed_by_kind:
            s["warnings"].append(f"Multiple {kind} inputs; using the first "
                                 f"({parsed_by_kind[kind]['file']}), ignoring {p.name}.")
            continue
        parsed_by_kind[kind] = {"file": p.name, "data": PARSERS[kind](text)}

    def get(kind):
        return parsed_by_kind[kind]["data"] if kind in parsed_by_kind else None

    meta = {**(get("design_info") or {}), **(get("build_metadata") or {})}
    states = {i["design_state"].lower().replace("fully ", "") for i in s["inputs"] if i["design_state"]}
    devices = {i["device"] for i in s["inputs"] if i["device"]}
    tools = {i["tool"] for i in s["inputs"] if i["tool"]}
    # Some reports omit the speed grade (xck26-sfvc784 vs xck26-sfvc784-2LV-c); only flag real conflicts.
    longest = max(devices, key=len) if devices else ""
    if any(not longest.startswith(d) for d in devices) or len(states) > 1:
        s["warnings"].append(f"Reports disagree: devices={sorted(devices)} states={sorted(states)}.")
    devices = {longest} if longest else set()

    if meta.get("evidence") == "out_of_context_synthesis":
        stage = "Out-of-context synthesis estimate (no place/route, no board wrapper)"
    elif "routed" in {x.lower() for x in states}:
        stage = "Post-route (implemented design)"
    elif "placed" in {x.lower() for x in states}:
        stage = "Post-placement estimate"
    elif "synthesized" in {x.lower() for x in states}:
        stage = "Post-synthesis estimate"
    else:
        stage = "Unknown (no design state in reports)"

    n = n_override or (int(meta["N"]) if str(meta.get("N", "")).isdigit() else None)
    lanes = int(meta["LANES"]) if str(meta.get("LANES", "")).isdigit() else None

    # Area: kernel row from the hierarchy if requested, else the flat/whole design.
    area, area_scope = {}, None
    hier = get("utilization_hier")
    if hier:
        if kernel:
            matches = [r for r in hier if not r["self_only"] and
                       (r["path"] == kernel or r["path"].endswith("/" + kernel) or
                        r["instance"] == kernel)]
            if matches:
                row = matches[0]
                area_scope = f"instance {row['path'] or row['instance']} ({row['module']})"
                if len(matches) > 1:
                    s["warnings"].append(f"Kernel '{kernel}' matched {len(matches)} rows; using first.")
            else:
                s["warnings"].append(f"Kernel instance '{kernel}' not found in hierarchical utilization.")
                row = None
        else:
            row = hier[0]
            area_scope = f"whole design ({row['instance']})"
        if row:
            area = {k: row.get(k) for k in HIER_COLUMNS}
    util = get("utilization")
    # Without a hierarchy report the flat totals are the whole design (e.g. OOC synthesis of the
    # kernel itself). Never substitute them for a named kernel the hierarchy report lacks.
    if not area and util and not (kernel and hier):
        area_scope = "whole design (flat utilization report)"
        area = {"Total LUTs": (util.get("CLB LUTs") or {}).get("used"),
                "LUTRAMs": (util.get("LUT as Distributed RAM") or {}).get("used"),
                "SRLs": (util.get("LUT as Shift Register") or {}).get("used"),
                "FFs": (util.get("CLB Registers") or {}).get("used"),
                "RAMB36": (util.get("RAMB36/FIFO*") or {}).get("used"),
                "RAMB18": (util.get("RAMB18") or {}).get("used"),
                "URAM": (util.get("URAM") or {}).get("used"),
                "DSP Blocks": (util.get("DSPs") or {}).get("used")}

    ts = get("timing_summary")
    timing = {}
    if ts:
        timing = {"constraints_met": ts["constraints_met"], **ts["design"],
                  "clocks": ts["clocks"], "check_timing": ts["check_timing"],
                  "worst_setup_paths": ts["worst_setup_paths"]}
        est = []
        for c in ts["clocks"]:
            intra = next((x for x in ts["intra_clock"] if x["clock"] == c["name"]), None)
            if intra and isinstance(intra["WNS"], (int, float)) and c["period_ns"] > intra["WNS"]:
                est.append({"clock": c["name"], "constrained_mhz": c["freq_mhz"],
                            "wns_ns": intra["WNS"],
                            "estimated_fmax_mhz": round(1000.0 / (c["period_ns"] - intra["WNS"]), 1)})
        timing["fmax_estimates"] = est
    kp = get("timing_paths")
    if kp:
        timing["kernel_worst_paths"] = kp[:3]

    pw = get("power")
    power = {}
    if pw:
        power = {k: pw.get(k) for k in ("total_w", "dynamic_w", "static_w", "junction_c", "confidence")}
        power["components"] = [c for c in pw["components"] if c["depth"] == 0]
        if kernel:
            krow = next((h for h in pw["hierarchy"] if h["path"] == kernel or
                         h["path"].endswith("/" + kernel)), None)
            power["kernel_w"] = krow["power_w"] if krow else None
            if not krow:
                power["kernel_note"] = ("not listed in the power hierarchy: Vivado omits blocks below "
                                        "about 0.001 W, or the block is deeper than the report depth")

    checks = {}
    for kind in ("drc", "methodology"):
        if get(kind):
            checks[kind] = get(kind)

    synth = get("synth_log")

    clock_period = None
    if meta.get("requested_period_ns"):
        clock_period = float(meta["requested_period_ns"])
    elif timing.get("clocks"):
        clock_period = timing["clocks"][0]["period_ns"]
    perf = {}
    if cycles:
        perf = {"cycles": cycles, "cycles_source": cycles_source}
        if clock_period:
            t_ns = cycles * clock_period
            perf.update({"clock_period_ns": clock_period, "kernel_time_us": round(t_ns / 1000, 3),
                         "time_basis": "cycles x constrained clock period (not a measured time)"})
            if n:
                macs = n ** 3
                perf.update({"macs": macs, "macs_per_cycle": round(macs / cycles, 3),
                             "gmac_per_s_at_constrained_clock": round(macs / t_ns, 3)})

    s.update({"stage": stage, "tool_versions": sorted(tools), "devices": sorted(devices),
              "metadata": meta, "N": n, "LANES": lanes, "kernel_instance": kernel,
              "area_scope": area_scope, "area": area, "timing": timing, "power": power,
              "checks": checks, "synthesis": synth, "performance": perf})
    return s


# ---------------------------------------------------------------- markdown
def fmt(v, unit=""):
    if v is None:
        return "n/a"
    if isinstance(v, float):
        v = f"{v:.3f}".rstrip("0").rstrip(".")
    return f"{v}{unit}"


def md_one(s):
    out = [f"## {s['label']}", "",
           f"- **Evidence stage:** {s['stage']}",
           f"- **Tool / device:** {', '.join(s['tool_versions']) or 'n/a'} / {', '.join(s['devices']) or s['metadata'].get('part', 'n/a')}"]
    if s["N"] or s["LANES"]:
        out.append(f"- **Configuration:** N={fmt(s['N'])}, LANES={fmt(s['LANES'])}, "
                   f"top={s['metadata'].get('top', 'n/a')}")
    for w in s["warnings"]:
        out.append(f"- **Warning:** {w}")
    out.append("")

    if s["area"]:
        out += [f"### Area ({s['area_scope']})", "", "| Resource | Used |", "|---|---|"]
        out += [f"| {k} | {fmt(v)} |" for k, v in s["area"].items() if v is not None]
        out.append("")

    t = s["timing"]
    if t:
        met = {True: "MET", False: "NOT MET", None: "unknown"}[t.get("constraints_met")]
        out += ["### Timing", "", f"- **Constraints:** {met}",
                f"- **Setup (WNS / TNS):** {fmt(t.get('WNS'), ' ns')} / {fmt(t.get('TNS'), ' ns')} "
                f"({fmt(t.get('TNS_failing'))} failing of {fmt(t.get('TNS_endpoints'))} endpoints)",
                f"- **Hold (WHS / THS):** {fmt(t.get('WHS'), ' ns')} / {fmt(t.get('THS'), ' ns')} "
                f"({fmt(t.get('THS_failing'))} failing)"]
        for c in t.get("clocks", []):
            out.append(f"- **Clock {c['name']}:** {fmt(c['period_ns'], ' ns')} "
                       f"({fmt(c['freq_mhz'], ' MHz')} constrained)")
        for e in t.get("fmax_estimates", []):
            out.append(f"- **Fmax estimate {e['clock']}:** about {fmt(e['estimated_fmax_mhz'], ' MHz')} "
                       "(1 / (period - WNS); a rough guide, not a verified frequency)")
        bad = {k: v for k, v in t.get("check_timing", {}).items() if v}
        if bad:
            out.append(f"- **check_timing issues:** {', '.join(f'{k}={v}' for k, v in bad.items())}")
        for label, key in (("Worst setup path", "worst_setup_paths"),
                           ("Worst kernel path", "kernel_worst_paths")):
            if t.get(key):
                p = t[key][0]
                out.append(f"- **{label}:** slack {fmt(p['slack_ns'], ' ns')}, "
                           f"{fmt(p.get('logic_levels'))} logic levels"
                           f"{' (' + p['logic_detail'] + ')' if p.get('logic_detail') else ''}, "
                           f"`{short(p.get('source'))}` -> `{short(p.get('destination'))}`")
        out.append("")

    p = s["power"]
    if p:
        out += ["### Power (Vivado estimate)", "",
                f"- **Total:** {fmt(p.get('total_w'), ' W')} (dynamic {fmt(p.get('dynamic_w'), ' W')}, "
                f"static {fmt(p.get('static_w'), ' W')}), junction {fmt(p.get('junction_c'), ' C')}, "
                f"confidence {fmt(p.get('confidence'))}"]
        if "kernel_w" in p:
            out.append(f"- **Kernel ({s['kernel_instance']}):** {fmt(p['kernel_w'], ' W')}"
                       f"{' (' + p['kernel_note'] + ')' if p.get('kernel_note') else ''}")
        comps = [f"{c['name']} {fmt(c['power_w'], ' W')}" for c in p.get("components", [])
                 if c["name"] not in ("Total",)]
        if comps:
            out.append(f"- **By component:** {'; '.join(comps)}")
        out += ["- Default activity estimate unless a simulation activity file was loaded; "
                "not a board measurement.", ""]

    if s["checks"]:
        out += ["### Design rule checks", ""]
        for kind, c in s["checks"].items():
            sev = ", ".join(f"{k}: {v}" for k, v in c["by_severity"].items()) or "none found"
            out.append(f"- **{kind.upper()}:** {sev}")
            for r in c["rules"]:
                if r["severity"].lower() in ("error", "critical warning"):
                    out.append(f"  - {r['severity']} {r['rule']}: {r['description']} ({r['checks']})")
        out.append("")

    sy = s["synthesis"]
    if sy:
        out += ["### Synthesis inference", ""]
        if "errors" in sy:
            out.append(f"- **Synthesis messages:** {sy['errors']} errors, "
                       f"{sy['critical_warnings']} critical warnings, {sy['warnings']} warnings")
        if sy["rtl_components"]:
            out.append("- **Inferred RTL components:** " + "; ".join(
                f"{c['category']}: {c['item']} x{c['count']}" for c in sy["rtl_components"]))
        if sy["cell_usage"]:
            out.append("- **Mapped primitives:** " + ", ".join(
                f"{k} {v}" for k, v in sy["cell_usage"].items()))
        for tbl in sy["mapping_tables"]:
            out += ["", f"**{tbl['title']}**", "",
                    "| " + " | ".join(tbl["header"]) + " |",
                    "|" + "---|" * len(tbl["header"])]
            out += ["| " + " | ".join(r) + " |" for r in tbl["rows"][:20]]
        out.append("")

    pf = s["performance"]
    if pf:
        out += ["### Kernel cycles", "",
                f"- **Cycles:** {pf['cycles']} (source: {pf['cycles_source']})"]
        if "kernel_time_us" in pf:
            out.append(f"- **Compute time at constrained clock:** {fmt(pf['kernel_time_us'], ' us')} "
                       f"({pf['time_basis']})")
        if "macs" in pf:
            out.append(f"- **Work:** {pf['macs']} multiply-accumulates; {fmt(pf['macs_per_cycle'])} per cycle; "
                       f"{fmt(pf['gmac_per_s_at_constrained_clock'])} GMAC/s at constrained clock")
        out.append("- Excludes operand loading, polling, readback and host transfer.")
        out.append("")

    out += ["<details><summary>Input files and SHA256</summary>", ""]
    out += [f"- `{Path(i['file']).name}` ({i['kind']}): `{i['sha256']}`" for i in s["inputs"]]
    out += ["", "</details>", ""]
    return out


def short(name, keep=3):
    if not name:
        return "n/a"
    parts = name.split("/")
    return name if len(parts) <= keep else ".../" + "/".join(parts[-keep:])


def md_compare(summaries):
    rows = [("Evidence stage", lambda s: s["stage"].split(" (")[0]),
            ("N / LANES", lambda s: f"{fmt(s['N'])} / {fmt(s['LANES'])}"),
            ("LUTs", lambda s: fmt(s["area"].get("Total LUTs"))),
            ("FFs", lambda s: fmt(s["area"].get("FFs"))),
            ("LUTRAM", lambda s: fmt(s["area"].get("LUTRAMs"))),
            ("BRAM36 / BRAM18", lambda s: f"{fmt(s['area'].get('RAMB36'))} / {fmt(s['area'].get('RAMB18'))}"),
            ("DSP", lambda s: fmt(s["area"].get("DSP Blocks"))),
            ("Timing met", lambda s: {True: "yes", False: "NO", None: "n/a"}[s["timing"].get("constraints_met")]),
            ("WNS / WHS (ns)", lambda s: f"{fmt(s['timing'].get('WNS'))} / {fmt(s['timing'].get('WHS'))}"),
            ("Fmax estimate (MHz)", lambda s: ", ".join(fmt(e["estimated_fmax_mhz"]) for e in s["timing"].get("fmax_estimates", [])) or "n/a"),
            ("Power total (W)", lambda s: fmt(s["power"].get("total_w"))),
            ("Cycles", lambda s: fmt(s["performance"].get("cycles"))),
            ("Compute time (us)", lambda s: fmt(s["performance"].get("kernel_time_us")))]
    out = ["## Comparison", "", "| Metric | " + " | ".join(s["label"] for s in summaries) + " |",
           "|---|" + "---|" * len(summaries)]
    for name, f in rows:
        out.append(f"| {name} | " + " | ".join(f(s) for s in summaries) + " |")
    out += ["", "Area columns describe each folder's area scope; check each section before comparing.", ""]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", help="report folder(s)")
    ap.add_argument("--kernel", help="hierarchical instance name of the block to highlight")
    ap.add_argument("--log", action="append", default=[],
                    help="extra synthesis log; with several folders, give one per folder in order")
    ap.add_argument("--cycles", type=int, action="append", default=[],
                    help="kernel cycle count (one per folder, or one for all)")
    ap.add_argument("--cycles-source", default="unspecified",
                    choices=["simulation", "board", "expected", "unspecified"])
    ap.add_argument("--n", type=int, help="matrix size N if not in build_metadata.txt")
    ap.add_argument("--label", action="append", default=[], help="column label per folder")
    ap.add_argument("--title", default="Vivado results summary")
    ap.add_argument("--out", help="output folder (default: the single input folder)")
    a = ap.parse_args(argv)

    if len(a.dirs) > 1 and not a.out:
        ap.error("--out is required with several folders")
    for d in a.dirs:
        if not Path(d).is_dir():
            ap.error(f"not a folder: {d}")
    if len(a.log) not in (0, len(a.dirs)) and len(a.dirs) > 1:
        ap.error("give one --log per folder")
    if len(a.cycles) not in (0, 1, len(a.dirs)):
        ap.error("give one --cycles for all folders or one per folder")

    summaries = []
    for i, d in enumerate(a.dirs):
        logs = [a.log[i]] if len(a.dirs) > 1 and a.log else (a.log if len(a.dirs) == 1 else [])
        cyc = a.cycles[i] if len(a.cycles) == len(a.dirs) else (a.cycles[0] if a.cycles else None)
        label = a.label[i] if i < len(a.label) else None
        summaries.append(summarize_dir(d, logs, a.kernel, cyc, a.cycles_source, a.n, label))
    for s in summaries:
        if not s["inputs"]:
            print(f"error: no recognisable Vivado reports in {s['folder']}", file=sys.stderr)
            return 2

    out = Path(a.out or a.dirs[0])
    out.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    md = [f"# {a.title}", "", f"Generated {now} by hw/tools/vivado_summary.py from Vivado report files. "
          "This restates tool estimates; it is not evidence of bitstream loading or board execution.", ""]
    if len(summaries) > 1:
        md += md_compare(summaries)
    for s in summaries:
        md += md_one(s)
    (out / "summary.md").write_text("\n".join(md), encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"schema": SCHEMA, "generated_at": now,
                                                  "summaries": summaries}, indent=2), encoding="utf-8")
    print(f"wrote {out / 'summary.md'} and {out / 'summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
