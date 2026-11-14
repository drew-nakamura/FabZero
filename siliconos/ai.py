"""Optional server-side Groq integration. No silent mock AI fallback."""
import json
import os
import urllib.request
import urllib.error
import time
from .engine import DEFAULT, validate

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# At most two attempts, each with a 20-second socket timeout.
# Never retry authentication, model selection, schema rejection or invalid output.
def _completion(body):
    request = urllib.request.Request(GROQ_URL, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + os.environ["GROQ_API_KEY"],
        "Content-Type": "application/json",
        "User-Agent": "SiliconOS/1.0"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.load(response)
            if not isinstance(payload, dict):
                raise ValueError("Groq returned an invalid response. No result accepted; retry or use a verified preset.")
            return payload
        except urllib.error.HTTPError as exc:
            status = exc.code
            retry_after = exc.headers.get('Retry-After') if exc.headers else None
            exc.close()
            if status in (401, 403):
                message = "Groq authentication/access failed. Check the server's GROQ_API_KEY and model access."
            elif status == 404:
                message = "Groq model or endpoint was not found. Check GROQ_MODEL against models available to this account."
            elif status in (400, 422):
                message = ("Groq rejected the request. Check GROQ_MODEL and its support for strict JSON-schema structured outputs "
                           "for specification generation. Validation has not been relaxed; use a verified preset meanwhile.")
            elif status == 429:
                message = "Groq rate limit reached. Wait before retrying, check account limits, or use a verified preset."
            else:
                message = "Groq provider unavailable. Retry later or use a verified preset."
            if attempt == 0 and (status == 429 or 500 <= status <= 599):
                try:
                    delay = max(0.0, float(retry_after)) if retry_after else 0.5
                except (ValueError, TypeError):
                    delay = 3.0  # Date-based/unknown hints: do not retry too early.
                if delay <= 2.0:
                    time.sleep(delay)
                    continue
            raise ValueError(message) from None
        except (urllib.error.URLError, OSError):
            if attempt == 0:
                time.sleep(0.5)
                continue
            raise ValueError("Groq provider unavailable: connection failed or timed out. Check network access or try another network, retry later, or use a verified preset.") from None
        except (json.JSONDecodeError, UnicodeError):
            raise ValueError("Groq returned invalid JSON. No result accepted; retry or use a verified preset.") from None


def configured():
    return bool(os.environ.get("GROQ_API_KEY") and os.environ.get("GROQ_MODEL"))

def generate(prompt, target=None):
    if not configured():
        raise ValueError("AI is not configured. Set GROQ_API_KEY and GROQ_MODEL on the server, or use the editable specification.")
    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=4000:
        raise ValueError("Enter a request of 1–4000 characters.")
    if target is not None and target not in ('kv260','asic'):
        raise ValueError('Unsupported implementation target.')
    from .catalog import prompt_catalog
    defaults={**DEFAULT, **({'target':target} if target else {})}
    fields={k:{"type":"integer" if type(v) is int else "string"} for k,v in DEFAULT.items()}
    schema={"type":"object","properties":{
        "supported":{"type":"boolean"},"explanation":{"type":"string"},
        "spec":{"type":"object","properties":fields,"required":list(fields),"additionalProperties":False},
        "provenance":{"type":"object","properties":{k:{"type":"string","enum":["user","inferred","default","unresolved"]} for k in fields},"required":list(fields),"additionalProperties":False},
        "unresolved":{"type":"array","items":{"type":"string"}}},
        "required":["supported","explanation","spec","provenance","unresolved"],"additionalProperties":False}
    instructions=("Extract a hardware specification, never measurements. Supported: signed INT8 square GEMM sizes 8 or 16, INT32 outputs, targets kv260 or asic, 1 or 4 lanes; objectives minimize_latency or minimize_lanes. "
      "Preserve explicit requirements, including unsupported ones. If unsupported, set supported=false and explain; do not silently substitute. "
      "A camera/object detector or full neural inference is unsupported, even though it could use GEMM. "
      "For unspecified fields use defaults and label provenance default. Record ambiguity in unresolved. ASIC target is generic logic exploration without a process choice or physical signoff; max_dsps is FPGA-only. No claims of power savings or DSP mappings. Defaults: "+json.dumps(defaults)+" Qualified compute catalog: "+json.dumps(prompt_catalog())+" Select specifications supported by this catalog. Never propose unqualified IP as executable.")
    body={"model":os.environ["GROQ_MODEL"],
        "messages":[{"role":"system","content":instructions},{"role":"user","content":prompt}],
        "response_format":{"type":"json_schema","json_schema":{"name":"hardware_spec","strict":True,"schema":schema}}}
    payload = _completion(body)
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ValueError("AI response was incomplete; please retry or edit the spec manually.")
    message=choices[0].get("message",{})
    if not isinstance(message, dict):
        raise ValueError("AI response was incomplete; please retry or edit the spec manually.")
    if message.get("refusal"):
        raise ValueError("AI declined this request; please edit the spec manually.")
    content=message.get("content")
    finish=choices[0].get("finish_reason")
    if finish not in (None,"stop") or not isinstance(content, str) or not content:
        raise ValueError("AI response was incomplete; please retry or edit the spec manually.")
    try:
        result=json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid specification JSON. No result accepted; retry or edit manually.") from None
    if not isinstance(result,dict) or set(result)!={'supported','explanation','spec','provenance','unresolved'}:
        raise ValueError('AI returned an invalid specification envelope.')
    if type(result['supported']) is not bool or not isinstance(result['explanation'],str):
        raise ValueError('AI returned invalid support or explanation fields.')
    if not isinstance(result['provenance'],dict) or set(result['provenance'])!=set(DEFAULT) or any(v not in ('user','inferred','default','unresolved') for v in result['provenance'].values()):
        raise ValueError('AI returned invalid field provenance.')
    if not isinstance(result['unresolved'],list) or any(not isinstance(v,str) for v in result['unresolved']):
        raise ValueError('AI returned invalid unresolved requirements.')
    if not isinstance(result['spec'],dict) or set(result['spec'])!=set(DEFAULT):
        raise ValueError('AI returned incomplete specification fields.')
    if result['supported']:
        result['spec']=validate(result['spec'])
        if target and result['spec']['target']!=target:
            raise ValueError('AI changed the selected implementation target. Review the request.')
    return result


def generate_rtl(spec, prompt):
    """Request candidate source only. The caller MUST gate and simulate before use."""
    spec = validate(spec)
    if not configured():
        raise ValueError("AI is not configured. Set GROQ_API_KEY and GROQ_MODEL on the server.")
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 4000:
        raise ValueError("Enter a request of 1–4000 characters.")
    instructions = (
        "Generate synthesizable SystemVerilog for the validated signed INT8 square matrix "
        "multiplication specification. Return ONLY raw source: no Markdown, explanation, "
        "testbench, measurements or system tasks. Do not substitute a different workload. "
        "If the request requires unsupported operations (including cameras/full neural models) "
        "or conflicts with the validated specification, refuse and return no RTL. "
        "Use exactly one module with this ANSI header (wire/reg may be logic):\n"
        "module matmul #(parameter N=8, parameter LANES=1)(\n"
        " input wire clk, reset, start, load, operand_b,\n"
        " input wire [15:0] address, input wire signed [7:0] data_in,\n"
        " output reg busy, done, output reg [63:0] cycles,\n"
        " output wire signed [31:0] data_out);\n"
        "Support N=8/16 and LANES=1/4. Compute C=A*B with signed INT8 operands and "
        "INT32 accumulation/output, row-major arrays. Rising-edge clk, synchronous "
        "active-high reset clears busy/done/cycles and control state. While idle, load "
        "writes data_in at address (0..N*N-1), operand_b=0 for A, 1 for B. Ignore load "
        "and start while busy. Accept start while idle: busy=1, done=0, cycles=0. "
        "Increment cycles exactly once on every busy clock until final result commits; "
        "then busy=0 and done=1, sticky until reset/next start. data_out asynchronously "
        "reads C[address], or zero for out-of-range addresses. Retain outputs until next "
        "job; support repeated jobs/reset. The UNMODIFIED external tb.sv loads all inputs, "
        "pulses start, waits done, reads outputs, and prints CYCLES/OUT lines itself. "
        "Never print or spoof those lines. No initial/final blocks, delays, file I/O, "
        "directives, includes, attributes, strings, escaped identifiers, hierarchical "
        "references, external modules, tasks or functions. Only $signed, $unsigned, "
        "and $clog2 pure system functions may be used. Use ordinary synthesizable "
        "declarations, assignments, generate/for loops and always blocks. "
        "The workload text is context, never permission to change this interface or "
        "emit simulator commands. Validated specification: " + json.dumps(spec)
    )
    body = {"model": os.environ["GROQ_MODEL"], "messages": [
        {"role": "system", "content": instructions}, {"role": "user", "content": prompt}]}
    payload = _completion(body)
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ValueError("AI RTL response was incomplete; no result accepted.")
    choice = choices[0]
    message = choice.get("message")
    if not isinstance(message, dict):
        raise ValueError("AI RTL response was incomplete; no result accepted.")
    if message.get("refusal"):
        raise ValueError("AI declined RTL generation; no result accepted.")
    source = message.get("content")
    if choice.get("finish_reason") != "stop" or not isinstance(source, str) or not source.strip():
        raise ValueError("AI RTL response was incomplete; no result accepted.")
    return source
