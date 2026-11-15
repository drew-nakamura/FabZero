# Board result file (local application contract)

Version 1, 2026-11-14 (America/Los_Angeles). Decision D-025. Replaces the website upload endpoint in DEMO_PRODUCT_AND_FPGA_SPEC.md §8.1 for the current demo. Keeps its §8.2 envelope, with the JTAG-specific values defined below. Items marked **TO AGREE** need the application owner's sign-off before either side relies on them.

## Who writes and who reads

- **Writer:** the fixed board runner (xsdb over JTAG from the build laptop), one folder per board run. It never edits an existing run folder.
- **Reader:** the local SiliconeOS application, which displays the result and independently re-checks it (§Acceptance). The application never edits runner files.

## Location and naming

```
hw/matmul_board/results/<run_id>/
  board-result.json     # the envelope below (the file the application reads)
  inputs.json           # {"A": [64 ints], "B": [64 ints]} exactly as loaded
  xsdb.log              # full raw xsdb transcript of the run
```

- `<run_id>` = `<UTC time YYYYMMDDTHHMMSSZ>_n<N>_l<LANES>`, for example `20261115T031500Z_n8_l1`. Sorting by name sorts by time.
- The runner writes into a temporary folder and renames it when complete, so the application never sees a half-written run. A failed run is still written, with `"status": "fail"` and the reason.
- Results are generated files, not source. Whether to commit selected runs is decided per demo (**TO AGREE**).

## board-result.json

Field names follow DEMO_PRODUCT_AND_FPGA_SPEC.md §8.2. Additions are marked (added).

```json
{
  "schema_version": 1,
  "runner_result_id": "uuid4",
  "parent_run_id": null,
  "status": "pass | fail",                                      // (added)
  "failure_reason": null,                                       // (added) text when status is fail
  "evidence": "board_measured",
  "recorded_at": "RFC3339 timestamp with offset",
  "workload_id": "e.g. identity-ramp-v1",                       // (added)
  "source_sha256": {"matmul.sv": "...", "matmul_axi.sv": "..."},
  "build": {
    "bitstream_sha256": "...",
    "vivado_version": "2025.2",
    "target_part": "xck26-sfvc784-2LV-c",
    "board_part": "xilinx.com:kv260_som:part0:1.4",            // (added)
    "top": "matmul_axi",
    "board_top": "actual integrated HDL top module",            // (added)
    "parameters": {"N": 8, "LANES": 1},
    "configured_clock_hz": 100000000,
    "timing_met": true,
    "implementation_manifest_sha256": "..."
  },
  "board": {
    "sku": "SK-KV260-G",
    "board_revision": "as read from the board, or null if not readable",
    "image_identity": "none: JTAG boot, no operating system",
    "kernel_version": null,
    "firmware_identity": "QSPI U-Boot 2023.01 (May 10 2024); bypassed by JTAG boot",
    "loader": "xsdb 2025.2 over JTAG (hw_server 2025.2)",
    "jtag_cable_serial": "FTDI serial, e.g. XFL13U31JOU3"       // (added)
  },
  "interface_check": {
    "base_address": "0x...",                                     // (added) from the build's address map
    "identity": 1397312513,
    "compiled_n": 8,
    "compiled_lanes": 1,
    "scratch_register_ok": true                                  // (added) 0x0c write 5/read 5/write 0/read 0
  },
  "run": {
    "input_sha256": "...",
    "outputs": [64 signed INT32 values, row-major],
    "output_sha256": "...",
    "expected_outputs_match": true,                              // (added) runner's own check
    "cycles": 512,
    "kernel_timing_boundary": "accelerator busy clocks",
    "host_elapsed_ns": 123456789,
    "programming_elapsed_ns": 123456789
  },
  "repeat_checks": {                                             // (added)
    "repeat_without_reload": {"outputs_match": true, "cycles": 512},
    "reset_reload_rerun": {"outputs_match": true, "cycles": 512}
  }
}
```

The `//` comments are explanation only; the real file is plain JSON without comments.

- `kernel_version: null` and `image_identity: "none: ..."` are deliberate. No operating system runs in the JTAG route, so nothing is invented.
- `host_elapsed_ns` covers operand loading, start, polling and readback over JTAG. It is expected to dwarf the kernel time and must never be presented as kernel speed.
- `parent_run_id` stays null until the local application creates parent simulation runs. **TO AGREE:** how the application links a board run to its parent.

## Hash rules (TO AGREE with the application owner before relying on hashes)

Proposed, so both sides compute the same values:

- `input_sha256` = SHA256 of the UTF-8 bytes of `{"A":[...],"B":[...]}`. Use row-major integers, no spaces (`separators=(",", ":")`), keys in that order.
- `output_sha256` = SHA256 of the UTF-8 bytes of `[...]`: the 64 outputs, no spaces.
- File hashes (`source_sha256`, `bitstream_sha256`) = SHA256 of the raw file bytes, lowercase hex.
- If the existing engine export already defines a different canonical form, use the engine's and update this file.

## Acceptance by the application

The application shows a run as physically verified only if all of these hold. It must not trust `status` alone.

1. `schema_version` is 1 and all required fields are present.
2. N and LANES in `build.parameters` equal `interface_check.compiled_n` / `compiled_lanes`.
3. `identity` = 1397312513 (0x53494c01).
4. It recomputes the expected outputs from `inputs.json` with its own reference model, and every output matches.
5. Recomputed `input_sha256` and `output_sha256` match.
6. `cycles` = N³ / LANES for the checked-in schedule (512 for 1 lane, 128 for 4 lanes).
7. `build.timing_met` is true and `bitstream_sha256` matches the implementation manifest.

Anything else is displayed as failed or unverified, with its reason. It is never relabeled as success.

## Recording

Per D-025, the presentation uses labeled recordings or screenshots of genuine runs instead of a live board run. Each must show the run folder name (`<run_id>`) or `runner_result_id`, and be labeled "Recorded real run" (plus "time-compressed" and the real duration if sped up).
