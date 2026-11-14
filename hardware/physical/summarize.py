"""Extract physical-run evidence without treating flow completion as signoff."""
import argparse
import hashlib
import json
from pathlib import Path


def summarize(run):
    run=Path(run)
    metrics=json.loads((run/'final/metrics.json').read_text())
    config=json.loads((run/'resolved.json').read_text())
    keys=['timing__setup__ws','timing__hold__ws','design__max_slew_violation__count',
          'design__max_cap_violation__count','design__max_fanout_violation__count',
          'route__antenna_violation__count','route__drc_errors','magic__drc_error__count',
          'klayout__drc_error__count','design__lvs_error__count']
    values={key:metrics.get(key) for key in keys}
    gds=run/'final/gds/matmul.gds'
    gds_sha256=hashlib.sha256(gds.read_bytes()).hexdigest() if gds.exists() else None
    checks={key:(None if value is None else value>=0 if key.startswith('timing__') else value==0) for key,value in values.items()}
    sources={Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in config['VERILOG_FILES']}
    return {'evidence':'post_route_flow_reports','run':run.name,'pdk':config['PDK'],
            'clock_period_ns':config['CLOCK_PERIOD'],'source_sha256':sources,
            'reported_instance_area_um2':metrics.get('design__instance__area'),
            'gds_sha256':gds_sha256,
            'metrics':values,'checks':checks,'all_listed_checks_pass':all(v is True for v in checks.values()),
            'fabrication_ready':False,'limitations':['Flow reports use the configured corners and I/O assumptions.',
             'Passing these listed checks is not a complete fabrication signoff.',
             'Power requires reviewed switching activity and operating assumptions.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run')
    print(json.dumps(summarize(parser.parse_args().run),indent=2))
