# Reduced-precision implementation and recovery notes

SiliconOS supports signed `int2`, `int4`, and `int8` square matrix multiplication with INT32 outputs. The default remains `int8`.

For `int2`, valid input values are `-2`, `-1`, `0`, and `1`; for `int4`, they are `-8` through `7`. The host and AXI-Lite load path remain byte wide for compatibility. The checked-in kernel stores each operand in `INPUT_BITS` bits and uses that width for signed multiplication; `INPUT_BITS=2`, `4`, or `8` for `int2`, `int4`, or `int8`.

The configuration path is:

`spec.precision` → `INPUT_BITS` in the simulator, generated RTL prompt, catalog recipe, generic synthesis, and FPGA handoff archive.

The generated RTL endpoint accepts 1, 2, or 4 lanes. Its generated-source gate requires an `INPUT_BITS` parameter with a literal default of 2, 4, or 8 and still fixes the external byte-wide `data_in` and INT32 `data_out` ports.

Run the focused verification after editing this feature:

```sh
python3 -m unittest discover -s tests -v
node --test tests/test_web.js
git diff --check
```

Reduced-precision simulation proves the recorded vectors and the integer oracle result. It does not establish an FPGA resource, timing, bandwidth, quantization-accuracy, or board-speed improvement. Use a Vivado implementation with the matching `INPUT_BITS`, then a matching board run, before claiming either hardware benefit or deployment readiness.
