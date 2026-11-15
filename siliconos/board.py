"""Authenticate and validate physical KV260 evidence from a trusted local runner."""
import argparse
import hashlib
import hmac
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from .engine import reference, validate

IDENTITY = 0x53494C01
HASH = re.compile(r"[0-9a-f]{64}")
ALLOWED_PARENT_EVIDENCE = {"rtl_simulation", "ai_generated_rtl"}
RUNNER_KEY_ENV = "SILICONOS_RUNNER_KEY"
RUNNER_KEY_ID_ENV = "SILICONOS_RUNNER_KEY_ID"


def _object(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object.")
    return value


def _exact_keys(value, keys, name):
    value = _object(value, name)
    missing, extra = set(keys)-set(value), set(value)-set(keys)
    if missing or extra:
        details=[]
        if missing: details.append("missing "+", ".join(sorted(missing)))
        if extra: details.append("unknown "+", ".join(sorted(extra)))
        raise ValueError(f"Invalid {name}: "+"; ".join(details)+".")
    return value


def _text(value, name, maximum=500):
    if not isinstance(value, str) or not value.strip() or len(value)>maximum:
        raise ValueError(f"{name} must be a nonempty string of at most {maximum} characters.")
    return value.strip()


def _hash(value, name):
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest.")
    return value


def _uuid(value, name):
    try: parsed=uuid.UUID(value)
    except (ValueError,TypeError,AttributeError):
        raise ValueError(f"{name} must be a UUID.") from None
    if str(parsed)!=value: raise ValueError(f"{name} must use canonical lowercase UUID form.")
    return value


def _timestamp(value):
    value=_text(value,"recorded_at",100)
    try: parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError: raise ValueError("recorded_at must be an RFC3339 timestamp.") from None
    if parsed.tzinfo is None: raise ValueError("recorded_at must include a timezone.")
    return value


def _optional_duration(value,name):
    if value is not None and (type(value) is not int or value<0):
        raise ValueError(f"{name} must be null or a nonnegative integer number of nanoseconds.")
    return value


def canonical_bytes(value):
    """Canonical UTF-8 JSON for manifests, signatures, and external hashes."""
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()


def payload_sha256(payload):
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def outputs_sha256(outputs):
    """Hash compact JSON UTF-8 output bytes, e.g. [1,-2,3]."""
    return hashlib.sha256(json.dumps(outputs,separators=(",",":")).encode()).hexdigest()


def _unsigned(payload):
    return {key:value for key,value in payload.items() if key!="runner_auth"}


def sign_payload(payload,key,key_id):
    """Return a JSON-safe copy authenticated with a runner-only HMAC key."""
    key=_text(key,RUNNER_KEY_ENV,4096); key_id=_text(key_id,RUNNER_KEY_ID_ENV,100)
    if len(key.encode())<32: raise ValueError(f"{RUNNER_KEY_ENV} must contain at least 32 UTF-8 bytes.")
    clean=json.loads(json.dumps(_unsigned(_object(payload,"board result"))))
    signature=hmac.new(key.encode(),canonical_bytes(clean),hashlib.sha256).hexdigest()
    clean["runner_auth"]={"key_id":key_id,"hmac_sha256":signature}
    return clean


def _authenticate(payload,runner_key=None,runner_key_id=None):
    runner_key=os.environ.get(RUNNER_KEY_ENV) if runner_key is None else runner_key
    runner_key_id=os.environ.get(RUNNER_KEY_ID_ENV) if runner_key_id is None else runner_key_id
    if not runner_key or not runner_key_id:
        raise ValueError(f"Trusted runner authentication is not configured. Set {RUNNER_KEY_ENV} and {RUNNER_KEY_ID_ENV} on the server.")
    auth=_exact_keys(payload.get("runner_auth"),{"key_id","hmac_sha256"},"runner_auth")
    if auth["key_id"]!=runner_key_id: raise ValueError("Board result runner key ID is not trusted by this server.")
    supplied=_hash(auth["hmac_sha256"],"runner_auth.hmac_sha256")
    expected=hmac.new(runner_key.encode(),canonical_bytes(_unsigned(payload)),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(supplied,expected): raise ValueError("Board result runner authentication failed.")
    return {"key_id":runner_key_id,"hmac_sha256":supplied}


def _validate_outputs(value,expected,name):
    if not isinstance(value,list) or len(value)!=len(expected) or any(type(x) is not int or not -(2**31)<=x<2**31 for x in value):
        raise ValueError(f"{name} must contain exactly {len(expected)} signed INT32 values.")
    if value!=expected: raise ValueError(f"{name} do not match the independent integer oracle.")
    return list(value)


def _validate_lifecycle_run(value,expected,expected_cycles,name):
    value=_exact_keys(value,{"outputs","output_sha256","cycles"},name)
    outputs=_validate_outputs(value["outputs"],expected,f"{name} outputs")
    digest=outputs_sha256(outputs)
    if _hash(value["output_sha256"],f"{name}.output_sha256")!=digest:
        raise ValueError(f"{name} output hash does not match its canonical output vector.")
    if value["cycles"]!=expected_cycles: raise ValueError(f"{name} must report {expected_cycles} hardware cycles.")
    return {"outputs":outputs,"output_sha256":digest,"cycles":expected_cycles}


def validate_result(parent,payload,runner_key=None,runner_key_id=None):
    """Return immutable board evidence after authentication and deterministic checks."""
    payload=_exact_keys(payload,{"schema_version","runner_result_id","parent_run_id","evidence","recorded_at","source_sha256","build","board","interface_check","run","lifecycle","runner_auth"},"board result")
    auth=_authenticate(payload,runner_key,runner_key_id)
    parent=_object(parent,"parent run"); parent_id=_uuid(parent.get("id"),"parent run id")
    if parent.get("correct") is not True or parent.get("evidence") not in ALLOWED_PARENT_EVIDENCE:
        raise ValueError("Board evidence requires a correctness-verified RTL simulation parent.")
    spec=validate(parent.get("spec"))
    if spec["target"]!="kv260": raise ValueError("Board evidence requires a KV260-targeted parent run.")
    lanes=parent.get("lanes")
    if type(lanes) is not int or lanes not in (1,2,4) or lanes>spec["max_lanes"]: raise ValueError("Parent run has an invalid lane configuration.")
    if payload["schema_version"]!=1: raise ValueError("Unsupported board result schema version.")
    runner_result_id=_uuid(payload["runner_result_id"],"runner_result_id")
    if payload["parent_run_id"]!=parent_id: raise ValueError("Board result does not match the selected parent run.")
    if payload["evidence"]!="board_measured": raise ValueError("Physical result evidence must be board_measured.")
    recorded_at=_timestamp(payload["recorded_at"])

    expected_sources=parent.get("source_sha256"); sources=_object(payload["source_sha256"],"source_sha256")
    if not isinstance(expected_sources,dict) or not expected_sources or sources!=expected_sources:
        raise ValueError("Board result source hashes do not match the verified parent run.")
    for name,digest in sources.items(): _text(name,"source filename",200); _hash(digest,f"source_sha256[{name}]")

    build=_exact_keys(payload["build"],{"bitstream_sha256","vivado_version","target_part","top","parameters","configured_clock_hz","timing_met","implementation_manifest","implementation_manifest_sha256"},"build")
    bitstream_hash=_hash(build["bitstream_sha256"],"bitstream_sha256")
    vivado_version=_text(build["vivado_version"],"vivado_version",100); target_part=_text(build["target_part"],"target_part",200)
    if build["top"]!="matmul_axi": raise ValueError("Board result top must be matmul_axi.")
    parameters=_exact_keys(build["parameters"],{"N","LANES"},"build parameters")
    if parameters!={"N":spec["size"],"LANES":lanes}: raise ValueError("Board build parameters do not match the parent run.")
    clock_hz=build["configured_clock_hz"]
    if type(clock_hz) is not int or not 1_000_000<=clock_hz<=1_000_000_000: raise ValueError("configured_clock_hz must be an integer from 1 MHz through 1 GHz.")
    if build["timing_met"] is not True: raise ValueError("A board-verified result requires the matching implementation to report timing met.")

    manifest=_exact_keys(build["implementation_manifest"],{"schema_version","bitstream_sha256","vivado_version","target_part","top","parameters","configured_clock_hz","timing_met","source_sha256","wrapper_sha256","reports"},"implementation_manifest")
    if manifest["schema_version"]!=1: raise ValueError("Unsupported implementation manifest schema version.")
    bound={"bitstream_sha256":bitstream_hash,"vivado_version":vivado_version,"target_part":target_part,"top":"matmul_axi","parameters":parameters,"configured_clock_hz":clock_hz,"timing_met":True,"source_sha256":sources}
    for key,expected in bound.items():
        if manifest[key]!=expected: raise ValueError(f"Implementation manifest {key} does not match the board result.")
    wrapper_hash=_hash(manifest["wrapper_sha256"],"implementation_manifest.wrapper_sha256")
    reports=_exact_keys(manifest["reports"],{"timing","utilization","drc"},"implementation reports")
    clean_reports={name:_hash(digest,f"implementation reports.{name}") for name,digest in reports.items()}
    manifest_hash=hashlib.sha256(canonical_bytes(manifest)).hexdigest()
    if _hash(build["implementation_manifest_sha256"],"implementation_manifest_sha256")!=manifest_hash:
        raise ValueError("Implementation manifest hash does not match its canonical JSON content.")

    hardware=_exact_keys(payload["board"],{"sku","board_revision","image_identity","kernel_version","firmware_identity","loader"},"board")
    if hardware["sku"]!="SK-KV260-G": raise ValueError("Board result must identify the SK-KV260-G target.")
    clean_board={"sku":hardware["sku"]}
    for key in ("board_revision","kernel_version"):
        clean_board[key]=None if hardware[key] is None else _text(hardware[key],key)
    for key in ("image_identity","firmware_identity","loader"):
        clean_board[key]=_text(hardware[key],key)

    interface=_exact_keys(payload["interface_check"],{"identity","compiled_n","compiled_lanes"},"interface_check")
    if interface["identity"]!=IDENTITY: raise ValueError("FPGA identity register did not match SiliconOS.")
    if interface["compiled_n"]!=spec["size"] or interface["compiled_lanes"]!=lanes: raise ValueError("FPGA compiled parameters do not match the verified parent run.")

    inputs=_object(parent.get("inputs"),"parent inputs"); expected_outputs=reference(inputs.get("a"),inputs.get("b"),spec["size"])
    expected_cycles=spec["size"]**3//lanes if parent["evidence"]=="rtl_simulation" else parent.get("cycles")
    if type(expected_cycles) is not int or expected_cycles<=0: raise ValueError("Parent run does not contain a valid observed cycle count.")
    run=_exact_keys(payload["run"],{"input_sha256","outputs","output_sha256","cycles","kernel_timing_boundary","host_elapsed_ns","programming_elapsed_ns"},"run")
    if run["input_sha256"]!=parent.get("input_sha256"): raise ValueError("Board input hash does not match the verified parent vectors.")
    _hash(run["input_sha256"],"input_sha256")
    outputs=_validate_outputs(run["outputs"],expected_outputs,"Board outputs"); output_hash=outputs_sha256(outputs)
    if _hash(run["output_sha256"],"output_sha256")!=output_hash: raise ValueError("Board output hash does not match the canonical output vector.")
    cycles=run["cycles"]
    if type(cycles) is not int or not 1<=cycles<2**63: raise ValueError("Board cycles must be a positive 63-bit integer.")
    if cycles!=expected_cycles:
        origin="checked-in schedule" if parent["evidence"]=="rtl_simulation" else "verified generated RTL"
        raise ValueError(f"Board cycles must match the {origin} count of {expected_cycles}.")
    boundary=_text(run["kernel_timing_boundary"],"kernel_timing_boundary",300)
    host_elapsed=_optional_duration(run["host_elapsed_ns"],"host_elapsed_ns"); programming_elapsed=_optional_duration(run["programming_elapsed_ns"],"programming_elapsed_ns")
    lifecycle=_exact_keys(payload["lifecycle"],{"repeat_without_reload","reset_recovery"},"lifecycle")
    clean_lifecycle={name:_validate_lifecycle_run(lifecycle[name],expected_outputs,expected_cycles,f"lifecycle.{name}") for name in ("repeat_without_reload","reset_recovery")}
    clean_manifest={**bound,"schema_version":1,"wrapper_sha256":wrapper_hash,"reports":clean_reports}

    normalized={"schema_version":1,"runner_result_id":runner_result_id,"runner_auth":auth,"parent_run_id":parent_id,"evidence":"board_measured","correct":True,"recorded_at":recorded_at,"spec":spec,"lanes":lanes,"parameters":{"N":spec["size"],"LANES":lanes},"physical_fpga":True,"physical_asic":False,"source_sha256":dict(sources),"input_sha256":run["input_sha256"],"output_sha256":output_hash,"outputs":outputs,"cycles":cycles,"run":{"input_sha256":run["input_sha256"],"outputs":outputs,"output_sha256":output_hash,"cycles":cycles,"kernel_timing_boundary":boundary,"host_elapsed_ns":host_elapsed,"programming_elapsed_ns":programming_elapsed},"lifecycle":clean_lifecycle,"configured_clock_hz":clock_hz,"measured_kernel_ns":cycles*1_000_000_000/clock_hz,"kernel_timing_boundary":boundary,"host_elapsed_ns":host_elapsed,"programming_elapsed_ns":programming_elapsed,"interface_check":dict(interface),"build":{"bitstream_sha256":bitstream_hash,"vivado_version":vivado_version,"target_part":target_part,"top":"matmul_axi","parameters":dict(parameters),"configured_clock_hz":clock_hz,"timing_met":True,"implementation_manifest":clean_manifest,"implementation_manifest_sha256":manifest_hash},"board":clean_board,"verification":"authenticated runner; complete outputs and lifecycle runs matched the independent Python integer oracle","limitations":["Kernel timing covers accelerator busy clocks only; operand loading and result retrieval are excluded.","The trusted runner authenticated the artifact/report identities; retain the matching files for audit.","This run establishes the recorded artifact and vectors, not production reliability or all possible inputs."]}
    normalized["runner_payload_sha256"]=payload_sha256(payload)
    return normalized


def main():
    parser=argparse.ArgumentParser(description="Sign a board-result JSON file for trusted local import.")
    parser.add_argument("input",help="Unsigned board-result JSON"); parser.add_argument("output",help="Destination for signed board-result JSON")
    args=parser.parse_args(); key=os.environ.get(RUNNER_KEY_ENV); key_id=os.environ.get(RUNNER_KEY_ID_ENV)
    if not key or not key_id: parser.error(f"Set {RUNNER_KEY_ENV} and {RUNNER_KEY_ID_ENV} in this process environment.")
    payload=json.loads(Path(args.input).read_text()); signed=sign_payload(payload,key,key_id)
    Path(args.output).write_text(json.dumps(signed,indent=2)+"\n")
    print(f"Signed board result for runner key {key_id}; secret was not printed.")


if __name__=="__main__": main()
