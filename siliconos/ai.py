"""Optional server-side Groq integration. No silent mock AI fallback."""
import json
import os
import urllib.request
from .engine import DEFAULT, validate

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def configured():
    return bool(os.environ.get("GROQ_API_KEY") and os.environ.get("GROQ_MODEL"))

def generate(prompt):
    if not configured():
        raise ValueError("AI is not configured. Set GROQ_API_KEY and GROQ_MODEL on the server, or use the editable specification.")
    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=4000:
        raise ValueError("Enter a request of 1–4000 characters.")
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
      "For unspecified fields use defaults and label provenance default. Record ambiguity in unresolved. ASIC target is generic logic exploration without a process choice or physical signoff; max_dsps is FPGA-only. No claims of power savings or DSP mappings. Defaults: "+json.dumps(DEFAULT))
    body={"model":os.environ["GROQ_MODEL"],
        "messages":[{"role":"system","content":instructions},{"role":"user","content":prompt}],
        "response_format":{"type":"json_schema","json_schema":{"name":"hardware_spec","strict":True,"schema":schema}}}
    request=urllib.request.Request(GROQ_URL,data=json.dumps(body).encode(),
       headers={"Authorization":"Bearer "+os.environ["GROQ_API_KEY"],"Content-Type":"application/json"})
    with urllib.request.urlopen(request,timeout=45) as response:
        payload=json.load(response)
    choices=payload.get("choices") or []
    if not choices:
        raise ValueError("AI response was incomplete; please retry or edit the spec manually.")
    message=choices[0].get("message",{})
    if message.get("refusal"):
        raise ValueError("AI declined this request; please edit the spec manually.")
    content=message.get("content")
    finish=choices[0].get("finish_reason")
    if finish not in (None,"stop") or not content:
        raise ValueError("AI response was incomplete; please retry or edit the spec manually.")
    result=json.loads(content)
    if result["supported"]: result["spec"]=validate(result["spec"])
    return result
