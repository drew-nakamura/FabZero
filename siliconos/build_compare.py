"""Read a fixed pair of local routed builds, failing closed on changed evidence."""
import hashlib
import json
import math
import re
from pathlib import Path
from .vivado import parse_utilization

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ('utilization.rpt', 'timing_summary.rpt')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def header(text, field):
    match = re.search(r'^\|\s*' + re.escape(field) + r'\s*:\s*(.+)$', text, re.M)
    if not match:
        raise ValueError(f'Missing report header: {field}.')
    return match.group(1).strip()


def timing_metrics(text):
    match = re.search(r'^\s*WNS\(ns\).*?\n[^\n]*\n([^\n]+)', text, re.M)
    if not match:
        raise ValueError('Missing routed design timing summary.')
    values = match.group(1).split()
    if len(values) != 12:
        raise ValueError('Invalid routed timing summary columns.')
    try:
        numbers = [float(v) for v in values]
    except ValueError as exc:
        raise ValueError('Invalid routed timing values.') from exc
    if any(not math.isfinite(v) for v in numbers):
        raise ValueError('Non-finite routed timing value.')
    result = dict(zip(('wns_ns','tns_ns','whs_ns','ths_ns','wpws_ns','tpws_ns'),
                      (numbers[i] for i in (0,1,4,5,8,9))))
    result['constraints_met'] = (all(numbers[i] >= 0 for i in (0,4,8)) and
                                 all(numbers[i] == 0 for i in (1,2,5,6,9,10)))
    return result


def compare_builds(build_root=None, rtl_root=None):
    build_root = Path(build_root) if build_root is not None else ROOT/'build/drew-branch'
    # The routed artifacts were built from this archived source snapshot. The
    # active hardware/ tree may contain later, unimplemented RTL experiments.
    rtl_root = Path(rtl_root) if rtl_root is not None else ROOT/'hw/matmul_board/rtl'
    sources = {name: digest((rtl_root/name).read_bytes()) for name in ('matmul.sv','matmul_axi.sv')}
    current_sources = {name: digest((ROOT/'hardware'/name).read_bytes())
                       for name in sources} if rtl_root == ROOT/'hw/matmul_board/rtl' else sources
    builds = []
    for lane in (1,4):
        build_id = f'n8_l{lane}'
        folder = build_root/build_id
        raw_manifest = (folder/'implementation_manifest.json').read_bytes()
        manifest = json.loads(raw_manifest)
        if not isinstance(manifest, dict):
            raise ValueError(f'{build_id}: manifest must be a JSON object.')
        if not isinstance(manifest.get('rtl'), dict) or not isinstance(manifest.get('report_sha256'), dict):
            raise ValueError(f'{build_id}: manifest is missing RTL or report hashes.')
        if manifest.get('schema') != 'fabzero.matmul_board.implementation_manifest/1':
            raise ValueError(f'{build_id}: unsupported implementation manifest.')
        if manifest.get('parameters') != {'N':8,'LANES':lane}:
            raise ValueError(f'{build_id}: build parameters do not match its slot.')
        if manifest.get('rtl',{}).get('sha256') != sources:
            raise ValueError(f'{build_id}: RTL hash mismatch. Archived matmul.sv or matmul_axi.sv differs from this build; no comparison values displayed.')
        if manifest.get('board_top') != 'matmul_board_top' or manifest.get('logical_top') != 'matmul_axi':
            raise ValueError(f'{build_id}: unexpected top modules.')
        reports, hashes = {}, {}
        for name in REPORTS:
            raw = (folder/'reports'/name).read_bytes()
            hashes[name] = digest(raw)
            if manifest.get('report_sha256',{}).get(name) != hashes[name]:
                raise ValueError(f'{build_id}: {name} hash mismatch. No comparison values displayed.')
            text = raw.decode('utf-8')
            if header(text,'Design State').lower() not in ('routed','fully routed'):
                raise ValueError(f'{build_id}: {name} is not routed evidence.')
            if header(text,'Design') != manifest['board_top']:
                raise ValueError(f'{build_id}: report design differs from manifest.')
            version = re.search(r'Vivado v\.([^\s]+)', header(text,'Tool Version'))
            if not version or version.group(1) != manifest.get('vivado_version'):
                raise ValueError(f'{build_id}: report Vivado version differs from manifest.')
            # Timing reports omit speed/package suffixes; check that prefix explicitly.
            device = header(text,'Device')
            part = manifest.get('target_part','')
            if not part or not (part == device or part.startswith(device+'-')):
                raise ValueError(f'{build_id}: report device differs from manifest.')
            reports[name] = text
        resources = parse_utilization(reports['utilization.rpt'])
        if any(resources[k] is None for k in ('lut','ff','dsp')):
            raise ValueError(f'{build_id}: missing whole-design resource count.')
        timing = timing_metrics(reports['timing_summary.rpt'])
        builds.append(dict(id=build_id,parameters=manifest['parameters'],stage='Routed',
                           vivado_version=manifest['vivado_version'],part=manifest['target_part'],
                           resources=resources,timing=timing,source_sha256=sources,
                           manifest_sha256=digest(raw_manifest),report_sha256=hashes,reports=reports))
    if builds[0]['part'] != builds[1]['part']:
        raise ValueError('Builds target different devices; comparison rejected.')
    return dict(evidence='routed_implementation_comparison',scope='whole design',builds=builds,
                rtl_source='archived board build snapshot',
                current_rtl_matches_build=current_sources==sources)
