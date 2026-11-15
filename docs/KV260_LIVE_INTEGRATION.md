# KV260 integration for the live demo

The verified app parent runs and Drew's matching physical result folders are already in this checkout. The app's importer uses a trusted local adapter to check the handoff ZIP, implementation files, and board values before signing. The server then checks the signed result against its saved parent run and the independent integer oracle.

## Import the recorded app-linked measurements

Start `python3 server.py` in a shell that has `SILICONOS_RUNNER_KEY` (at least 32 bytes) and `SILICONOS_RUNNER_KEY_ID` set. Use the same two variables in the import shell. Keep the key outside Git. Then, from the repository root:

```sh
python3 -m siliconos.import_drew \
  hw/matmul_board/results/20261115T011930Z_n8_l1 \
  hw/matmul_board/build/n8_l1 \
  data/handoff_exports/siliconos-6bccf63e-f83a-4e12-88e6-78b20d120b65-n8-l1-handoff.zip

python3 -m siliconos.import_drew \
  hw/matmul_board/results/20261115T012007Z_n8_l4 \
  hw/matmul_board/build/n8_l4 \
  data/handoff_exports/siliconos-3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9-n8-l4-handoff.zip
```

The adapter rejects mismatched or missing `.bit` and report files. Both recorded results are for N=8, with 512 cycles at one lane and 128 cycles at four lanes. The bitstreams were built with Vivado 2025.2, and their reported configured PL clock is 99,999,001 Hz. Clock frequency was not independently measured. Host JTAG time includes transfer and programming and is separate from kernel cycles.

## Run a fresh app handoff on the board

Use the Windows computer with Vivado/XSDB 2025.2. Connect a USB data cable to KV260 J4 and 12 V power to J12, remove the SD card, and close Vivado Hardware Manager before using XSDB. In the repo on that computer:

```sh
python hw/matmul_board/run_board.py --check
python hw/matmul_board/run_board.py --handoff PATH_TO_APP_HANDOFF.zip
```

The current pinned bitstreams support the exact checked-in kernel and AXI wrapper at N=8, LANES=1 or 4. A changed source hash, including a line-ending change, will be rejected. The adapter needs the returned result folder, its matching `build/n8_l*` folder, and the original handoff ZIP. Copy those files back and run the import command above with the fresh paths. A new RTL build requires `python hw/matmul_board/build.py --handoff PATH_TO_APP_HANDOFF.zip` on the Vivado computer, then the board run. Treat that as a separate implementation with its own bitstream hash.

The recorded app-linked folders are physical board evidence reported by Drew's runner and logs. This checkout has not rerun the board independently. Show recorded results as recorded, with their parent run and bitstream identities visible.
