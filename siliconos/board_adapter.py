"""Verify a partner result folder and convert it to the signed app contract."""
import hashlib
import json
import os
from pathlib import Path

from . import board


def adapt_drew_result(result_file, build_dir, handoff_zip, *, runner_key=None, runner_key_id=None):
    result_file, build_dir, handoff_zip = map(Path, (result_file, build_dir, handoff_zip))
    def digest(data):
        return hashlib.sha256(data).hexdigest()

    def require(ok, message):
        if not ok:
            raise ValueError(message)

    def checked(root, name, expected):
        require(isinstance(name, str) and name and Path(name).name == name,
                "Unsafe artifact filename.")
        path = root / name
        require(path.is_file() and digest(path.read_bytes()) == expected,
                f"Artifact hash mismatch: {name}.")

    raw_bytes = result_file.read_bytes()
    raw = json.loads(raw_bytes)
    manifest_path = build_dir / "implementation_manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    require(digest(manifest_bytes) == raw["build"]["implementation_manifest_sha256"],
            "Implementation manifest hash mismatch.")
    require(manifest["schema"] == "fabzero.matmul_board.implementation_manifest/1" and
            manifest["timing"]["timing_met"] is True and manifest["drc_clean"] is True,
            "Implementation timing, DRC, or schema mismatch.")
    bits = list(build_dir.glob("*.bit"))
    require(len(bits) == 1 and digest(bits[0].read_bytes()) == manifest["bitstream_sha256"]
            == raw["build"]["bitstream_sha256"], "Actual bitstream hash mismatch.")
    reports = manifest["report_sha256"]
    require(isinstance(reports, dict) and reports and
            {"timing_summary.rpt", "utilization.rpt", "drc.rpt"} <= reports.keys(),
            "Implementation reports incomplete.")
    for name, expected in reports.items():
        checked(build_dir / "reports", name, expected)
    artifacts = manifest["artifacts_sha256"]
    require(isinstance(artifacts, dict) and artifacts.get(bits[0].name) ==
            manifest["bitstream_sha256"], "Bitstream artifact hash missing.")
    for name, expected in artifacts.items():
        checked(build_dir / ("summary" if name == "summary.json" else "."),
                name, expected)
    for raw_name, manifest_name in (("vivado_version", "vivado_version"),
                                    ("target_part", "target_part"),
                                    ("parameters", "parameters"),
                                    ("configured_clock_hz", "configured_clock_hz")):
        require(raw["build"][raw_name] == manifest[manifest_name],
                f"Build {raw_name} mismatch.")
    require(raw["build"]["top"] == manifest["logical_top"] == "matmul_axi" and
            raw["build"]["board_top"] == manifest["board_top"] == "matmul_board_top",
            "Build top mismatch.")
    import zipfile
    zip_bytes = handoff_zip.read_bytes()
    require(raw["handoff"]["zip_sha256"] == digest(zip_bytes),
            "Board result ZIP hash mismatch.")
    if manifest.get("handoff") is not None:
        require(manifest["handoff"]["zip_sha256"] == digest(zip_bytes) and
                manifest["handoff"]["parent_run_id"] == raw["parent_run_id"],
                "Build handoff mismatch.")
    with zipfile.ZipFile(handoff_zip) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and "manifest.json" in names,
                "ZIP inventory invalid.")
        zmanifest = json.loads(archive.read("manifest.json"))
        listed = zmanifest["files_sha256"]
        require(set(names) == set(listed) | {"manifest.json"},
                "ZIP inventory mismatch.")
        for name, expected in listed.items():
            require(not name.startswith("/") and ".." not in Path(name).parts and
                    digest(archive.read(name)) == expected,
                    f"ZIP entry hash mismatch: {name}.")
        zexpected = json.loads(archive.read("expected.json"))
    require(zmanifest["run_id"] == raw["parent_run_id"] and
            zmanifest["source_evidence"] == raw["handoff"]["source_evidence"]
            == "rtl_simulation", "ZIP parent mismatch.")
    require(raw["source_sha256"] == {
        "matmul.sv": listed["hardware/matmul.sv"],
        "tb.sv": listed["hardware/tb.sv"]} and
        raw["wrapper_sha256"] == listed["integration/matmul_axi.sv"],
        "ZIP source mismatch.")
    require(manifest["rtl"]["sha256"] == {
        "matmul.sv": listed["hardware/matmul.sv"],
        "matmul_axi.sv": listed["integration/matmul_axi.sv"]},
        "Build RTL source mismatch.")
    if manifest.get("handoff") is not None:
        for name, expected in manifest["rtl"]["sha256"].items():
            checked(build_dir / "rtl", name, expected)
    n, lanes = raw["build"]["parameters"]["N"], raw["build"]["parameters"]["LANES"]
    zip_parameters = zmanifest["parameters"]
    expected_parameters = zexpected["parameters"]
    require(n == 8 and lanes in (1, 4) and
            zip_parameters == expected_parameters and
            {key: zip_parameters[key] for key in ("N", "LANES")} ==
            raw["build"]["parameters"] == manifest["parameters"] and
            set(zip_parameters) <= {"N", "LANES", "INPUT_BITS"} and
            zip_parameters.get("INPUT_BITS", 8) == 8,
            "Build parameter mismatch.")
    a, b = zexpected["inputs"]["a"], zexpected["inputs"]["b"]
    require(all(isinstance(v, list) and len(v) == n*n and
                all(type(x) is int and -128 <= x <= 127 for x in v)
                for v in (a, b)), "Invalid ZIP inputs.")
    require(json.loads((result_file.parent / "inputs.json").read_bytes()) ==
            {"A": a, "B": b}, "Raw input file mismatch.")
    outputs = [sum(a[i*n+k]*b[k*n+j] for k in range(n))
               for i in range(n) for j in range(n)]
    cycles = n**3 // lanes
    require(zexpected["outputs"] == outputs and zexpected["cycles"] == cycles and
            raw["handoff"]["parent_expected_cycles"] == cycles and
            raw["handoff"]["parent_expected_outputs_match"] is True,
            "ZIP expected outputs or cycles mismatch.")
    run = raw["run"]
    require(run["input_sha256"] == digest(bytes(x & 255 for x in a+b)) and
            run["outputs"] == outputs and run["output_sha256"] ==
            board.outputs_sha256(outputs) and run["cycles"] == cycles,
            "Board run vectors or cycles mismatch.")
    for name in ("repeat_without_reload", "reset_reload_rerun"):
        repeat = raw["repeat_checks"][name]
        require(repeat["outputs"] == outputs and repeat["cycles"] == cycles,
                f"Board {name} mismatch.")
    interface = raw["interface_check"]
    require(interface["identity"] == board.IDENTITY and
            interface["compiled_n"] == n and interface["compiled_lanes"] == lanes and
            interface["base_address"] == manifest["address_map"]["base_address"],
            "Board interface mismatch.")
    require(raw["board"]["sku"] == zmanifest["board_sku"] == "SK-KV260-G"
            and raw["workload_id"] == "siliconos-run-" + raw["parent_run_id"],
            "Board identity or workload mismatch.")

    transcript = (result_file.parent / "xsdb.log").read_text(errors="replace")
    lines = [line.strip() for line in transcript.splitlines()]
    require(lines and lines[0].startswith(f"MM BEGIN n={n} ") and
            lines[-1] == "MM END" and
            f"MM ID {interface['identity']}" in lines and
            f"MM LANES {lanes}" in lines,
            "Board JTAG transcript identity mismatch.")
    for raw_name, log_name in (("first", "first"), ("repeat_without_reload", "repeat"),
                               ("reset_reload_rerun", "reset_reload")):
        measured = run if raw_name == "first" else raw["repeat_checks"][raw_name]
        require(f"MM OUT {log_name} " + " ".join(map(str, measured["outputs"])) in lines and
                any(line.startswith(f"MM JOB {log_name} ") and
                    f"cycles_lo={measured['cycles']} " in line and "timeout=0" in line
                    for line in lines),
                f"Board JTAG transcript {log_name} mismatch.")

    if raw.get("status") != "pass" or raw.get("evidence") != "board_measured":
        raise ValueError("Only a passing physical board result can be imported.")
    if raw.get("interface_check", {}).get("scratch_register_ok") is not True:
        raise ValueError("Board interface scratch-register check failed.")
    if raw.get("run", {}).get("expected_outputs_match") is not True:
        raise ValueError("Board first-run output check failed.")
    repeats = raw["repeat_checks"]
    if any(repeats[name].get("outputs_match") is not True
           for name in ("repeat_without_reload", "reset_reload_rerun")):
        raise ValueError("Board lifecycle output check failed.")

    b = raw["build"]
    source = raw["source_sha256"]
    report_hashes = manifest["report_sha256"]
    app_manifest = {
        "schema_version": 1,
        "bitstream_sha256": b["bitstream_sha256"],
        "vivado_version": b["vivado_version"],
        "target_part": b["target_part"],
        "top": b["top"],
        "parameters": b["parameters"],
        "configured_clock_hz": b["configured_clock_hz"],
        "timing_met": b["timing_met"],
        "source_sha256": source,
        "wrapper_sha256": raw["wrapper_sha256"],
        "reports": {name: report_hashes[file] for name, file in
                    (("timing", "timing_summary.rpt"),
                     ("utilization", "utilization.rpt"), ("drc", "drc.rpt"))},
    }
    run = raw["run"]
    lifecycle = {}
    for destination, origin in (("repeat_without_reload", "repeat_without_reload"),
                                ("reset_recovery", "reset_reload_rerun")):
        item = repeats[origin]
        lifecycle[destination] = {
            "outputs": item["outputs"],
            "output_sha256": board.outputs_sha256(item["outputs"]),
            "cycles": item["cycles"],
        }
    payload = {
        "schema_version": 1,
        "runner_result_id": raw["runner_result_id"],
        "parent_run_id": raw["parent_run_id"],
        "evidence": "board_measured",
        "recorded_at": raw["recorded_at"],
        "source_sha256": source,
        "build": {**{key: app_manifest[key] for key in
                     ("bitstream_sha256", "vivado_version", "target_part", "top",
                      "parameters", "configured_clock_hz", "timing_met")},
                  "implementation_manifest": app_manifest,
                  "implementation_manifest_sha256": hashlib.sha256(board.canonical_bytes(app_manifest)).hexdigest()},
        "board": {key: raw["board"][key] for key in
                  ("sku", "board_revision", "image_identity", "kernel_version", "firmware_identity", "loader")},
        "interface_check": {key: raw["interface_check"][key] for key in
                            ("identity", "compiled_n", "compiled_lanes")},
        "run": {key: run[key] for key in
                ("input_sha256", "outputs", "output_sha256", "cycles", "kernel_timing_boundary",
                 "host_elapsed_ns", "programming_elapsed_ns")},
        "lifecycle": lifecycle,
    }
    key = runner_key if runner_key is not None else os.environ.get(board.RUNNER_KEY_ENV)
    key_id = runner_key_id if runner_key_id is not None else os.environ.get(board.RUNNER_KEY_ID_ENV)
    if not key or not key_id:
        raise ValueError("Set SILICONOS_RUNNER_KEY and SILICONOS_RUNNER_KEY_ID in the importer process.")
    return board.sign_payload(payload, key, key_id)
