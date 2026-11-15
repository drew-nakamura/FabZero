"""Parse resource counts from a Vivado utilization report, without estimating them."""
import re
import hashlib
import json
from pathlib import Path


_INTEGER = re.compile(r"\d+(?:,\d{3})*")
_RESOURCES = {
    "lut": ("CLB LUTs", "Slice LUTs"),
    "ff": ("CLB Registers", "Slice Registers"),
    "bram": ("Block RAM Tile",),
}


def _rows(report):
    rows = {}
    for line in report.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not _INTEGER.fullmatch(cells[1]):
            continue
        name = cells[0]
        if name not in {"DSPs", "DSP48E1", "DSP48E2", "CLB LUTs", "Slice LUTs", "CLB Registers", "Slice Registers", "Block RAM Tile"}:
            continue
        value = int(cells[1].replace(",", ""))
        if name in rows and rows[name] != value:
            raise ValueError(f"Conflicting Vivado utilization rows for {name}.")
        rows[name] = value
    return rows


def _one_of(rows, names, resource):
    found = [(name, rows[name]) for name in names if name in rows]
    if not found:
        return None
    if len({value for _, value in found}) > 1:
        raise ValueError(f"Conflicting Vivado {resource} counts: {found}.")
    return found[0][1]


def parse_utilization(report):
    """Return {'dsp','lut','ff','bram'}; missing optional counts are None.

    DSP count must be an explicit DSPs or DSP48E1/E2 row. The function does not
    bind the report to any source, part, tool version, or stage: callers must do
    that before presenting a count as evidence.
    """
    if not isinstance(report, str) or not report.strip():
        raise ValueError("Vivado utilization report must be nonempty text.")
    rows = _rows(report)
    primitives = [rows[name] for name in ("DSP48E1", "DSP48E2") if name in rows]
    primitive_count = sum(primitives) if primitives else None
    summary_count = rows.get("DSPs")
    if summary_count is None and primitive_count is None:
        raise ValueError("Vivado utilization report has no explicit DSP count row.")
    if summary_count is not None and primitive_count is not None and summary_count != primitive_count:
        raise ValueError("Vivado DSP summary and primitive rows disagree.")
    result = {"dsp": summary_count if summary_count is not None else primitive_count}
    for resource, names in _RESOURCES.items():
        result[resource] = _one_of(rows, names, resource)
    return result


def parse_import(report, metadata):
    """Read user-supplied out-of-context synthesis evidence, without certifying it."""
    if not isinstance(metadata, str) or len(metadata) > 8192:
        raise ValueError('Vivado build metadata must be text under 8 KiB.')
    if metadata.lstrip().startswith('{'):
        try:
            manifest = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise ValueError('Invalid Vivado implementation manifest JSON.') from exc
        if not isinstance(manifest, dict) or manifest.get('schema') != 'fabzero.matmul_board.implementation_manifest/1':
            raise ValueError('Unsupported Vivado implementation manifest.')
        parameters = manifest.get('parameters')
        if not isinstance(parameters, dict) or parameters.get('N') not in (8, 16) or parameters.get('LANES') not in (1, 2, 4):
            raise ValueError('Unsupported implementation parameters.')
        expected_hash = manifest.get('report_sha256', {}).get('utilization.rpt')
        actual_hash = hashlib.sha256(report.encode()).hexdigest()
        if not expected_hash or expected_hash != actual_hash:
            raise ValueError('Utilization report does not match the implementation manifest hash.')
        source_hashes = manifest.get('rtl', {}).get('sha256', {})
        if not isinstance(source_hashes, dict) or not all(source_hashes.get(name) == hashlib.sha256((Path(__file__).resolve().parent.parent / 'hardware' / name).read_bytes()).hexdigest() for name in ('matmul.sv', 'matmul_axi.sv')):
            raise ValueError('Implementation RTL hashes do not match this checkout.')
        if manifest.get('logical_top') != 'matmul_axi' or manifest.get('board_top') != 'matmul_board_top':
            raise ValueError('Unexpected implementation top modules.')
        if not manifest.get('target_part') or not manifest.get('vivado_version'):
            raise ValueError('Implementation part or Vivado version is missing.')
        return {'evidence': 'user_imported_vivado_implementation', 'parameters': parameters,
                'part': manifest['target_part'], 'vivado_version': manifest['vivado_version'],
                'resources': parse_utilization(report), 'report_sha256': actual_hash,
                'metadata_sha256': hashlib.sha256(metadata.encode()).hexdigest(),
                'source_binding_verified': True, 'physical_fpga': False,
                'timing_closed': bool(manifest.get('timing', {}).get('timing_met')),
                'scope': 'whole board design',
                'limitations': ['User-supplied Vivado implementation and report; source and report hashes match this checkout.',
                                'The utilization count is for the whole board design, not only the kernel.',
                                'This import is not proof of physical board execution.']}
    fields = {}
    for line in metadata.splitlines():
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        if key in fields and fields[key] != value.strip():
            raise ValueError('Conflicting Vivado build metadata.')
        fields[key] = value.strip()
    required = ('evidence', 'vivado', 'top', 'part', 'N', 'LANES', 'source',
                'physical_fpga', 'timing_closed')
    if any(not fields.get(key) for key in required):
        raise ValueError('Vivado build metadata is incomplete.')
    if fields['evidence'] != 'out_of_context_synthesis' or fields['top'] != 'matmul':
        raise ValueError('Only kernel out-of-context synthesis is supported here.')
    if fields['physical_fpga'] != 'false' or fields['timing_closed'] != 'false':
        raise ValueError('Unexpected physical-status claims in build metadata.')
    try:
        n, lanes = int(fields['N']), int(fields['LANES'])
    except ValueError as exc:
        raise ValueError('Invalid Vivado build parameters.') from exc
    if n not in (8, 16) or lanes not in (1, 2, 4):
        raise ValueError('Unsupported Vivado build parameters.')
    resources = parse_utilization(report)
    return {'evidence': 'user_imported_vivado_ooc_synthesis', 'parameters': {'N': n, 'LANES': lanes},
            'part': fields['part'], 'vivado_version': fields['vivado'], 'resources': resources,
            'report_sha256': hashlib.sha256(report.encode()).hexdigest(),
            'metadata_sha256': hashlib.sha256(metadata.encode()).hexdigest(),
            'source_binding_verified': False, 'physical_fpga': False, 'timing_closed': False,
            'limitations': ['User-supplied synthesis report and metadata; source-to-report binding is not independently verified.',
                            'Out-of-context utilization is not a whole-board resource count or implementation result.',
                            'DSP budget and clock feasibility are not certified by this import.']}
