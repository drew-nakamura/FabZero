"""Allowlisted reusable RTL recipes. Research candidates are never executable."""
import hashlib
import json
from pathlib import Path
from .engine import ROOT, validate

ENGINE_IDS = {1: 'siliconos.matmul.serial.v1', 4: 'siliconos.matmul.parallel4.v1'}

def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def blocks():
    result=[]
    for lanes, identifier in ENGINE_IDS.items():
        result.append(dict(id=identifier,kind='compute',operation='matrix_multiply',
            precision='int8',accumulator='int32',sizes=[8,16],lanes=lanes,
            targets=['kv260','asic'],license='MIT',source='hardware/matmul.sv',
            source_sha256=digest('hardware/matmul.sv'),
            qualification='RTL regression and generic netlist simulation; physical deployment pending',
            runnable=True))
    vendor=ROOT/'hardware/vendor/wb2axip'
    manifest=json.loads((vendor/'manifest.json').read_text())
    intact=digest('hardware/vendor/wb2axip/skidbuffer.v')==manifest['source_sha256']
    result.append(dict(id='zipcpu.skidbuffer.registered8.v1',kind='stream_utility',
        runnable=False,standalone_only=True,source_integrity=intact,
        qualification='Standalone local protocol regression; not integrated into compute recipes',
        **manifest))
    return result

def prompt_catalog():
    return [{'id':b['id'],'operation':b['operation'],'sizes':b['sizes'],
             'lanes':b['lanes'],'targets':b['targets']} for b in blocks() if b['runnable']]

def plan(spec, lanes=None, block_id=None):
    spec=validate(spec)
    if block_id is not None:
        choices={v:k for k,v in ENGINE_IDS.items()}
        if not isinstance(block_id,str) or block_id not in choices:
            raise ValueError('Unknown or unqualified compute block. Select a catalog engine.')
        if lanes is not None and lanes!=choices[block_id]:
            raise ValueError('Block and lane selection disagree.')
        lanes=choices[block_id]
    if lanes is None:
        lanes=1 if spec['objective']=='minimize_lanes' else spec['max_lanes']
    if type(lanes) is not int or lanes not in ENGINE_IDS or lanes>spec['max_lanes']:
        raise ValueError('Unsupported catalog lane configuration.')
    files=['hardware/matmul.sv','hardware/tb.sv']
    recipe=dict(schema_version=1,block_id=ENGINE_IDS[lanes],spec=spec,
        parameters={'N':spec['size'],'LANES':lanes},
        source_sha256={p:digest(p) for p in files},license='MIT',
        source_files={p:(ROOT/p).read_text() for p in files},
        selection='deterministic constraint selection; no generated RTL',
        evidence='build_plan',physical_ready=False,
        limitations=['Planning is not execution or synthesis evidence.',
                    'Imported stream utility is not part of this compute recipe.',
                    'Lane scaling is not a fixed-resource optimization.'])
    identity={k:recipe[k] for k in ('schema_version','block_id','spec','parameters','source_sha256')}
    recipe['recipe_sha256']=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return recipe
