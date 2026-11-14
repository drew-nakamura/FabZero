"""Optional server-side OpenAI integration. No silent mock AI fallback."""
import json
import os
import urllib.request
from .engine import DEFAULT, validate

def configured():
    return bool(os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_MODEL"))

def generate(prompt):
    if not configured():
        raise ValueError("AI is not configured. Set OPENAI_API_KEY and OPENAI_MODEL on the server, or use the editable specification.")
    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=4000:
        raise ValueError("Enter a request of 1–4000 characters.")
    fields={k:{"type":"integer" if type(v) is int else "string"} for k,v in DEFAULT.items()}
    schema={"type":"object","properties":{
        "supported":{"type":"boolean"},"explanation":{"type":"string"},
        "spec":{"type":"object","properties":fields,"required":list(fields),"additionalProperties":False},
        "provenance":{"type":"object","properties":{k:{"type":"string","enum":["user","inferred","default","unresolved"]} for k in fields},"required":list(fields),"additionalProperties":False},
        "unresolved":{"type":"array","items":{"type":"string"}}},
        "required":["supported","explanation","spec","provenance","unresolved"],"additionalProperties":False}
    instructions=("Extract a hardware specification, never measurements. Supported: signed INT8 square GEMM sizes 8 or 16, INT32 outputs, KV260, 1 or 4 lanes; objectives minimize_latency or minimize_lanes. "
      "Preserve explicit requirements, including unsupported ones. If unsupported, set supported=false and explain; do not silently substitute. "
      "A camera/object detector or full neural inference is unsupported, even though it could use GEMM. "
      "For unspecified fields use defaults and label provenance default. Record ambiguity in unresolved. No claims of power savings or DSP mappings. Defaults: "+json.dumps(DEFAULT))
    body={"model":os.environ["OPENAI_MODEL"],"instructions":instructions,"input":prompt,
        "text":{"format":{"type":"json_schema","name":"hardware_spec","strict":True,"schema":schema}}}
    request=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),
       headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"})
    with urllib.request.urlopen(request,timeout=45) as response:
        payload=json.load(response)
    if payload.get("status")!="completed":
        raise ValueError("AI response was incomplete; please retry or edit the spec manually.")
    texts=[c["text"] for item in payload.get("output",[]) for c in item.get("content",[]) if c.get("type")=="output_text"]
    if not texts: raise ValueError("AI did not return a specification.")
    result=json.loads("".join(texts))
    if result["supported"]: result["spec"]=validate(result["spec"])
    return result
