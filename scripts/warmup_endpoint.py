#!/usr/bin/env python3
"""Bounded post-startup warmup for representative FlashNext prompt shapes."""
import argparse, concurrent.futures, json, time, urllib.request
from pathlib import Path

CODE = "def merge(a,b): return {**a, **b}\n"
def post(base, model, chars, timeout):
    body = (CODE * (chars // len(CODE) + 1))[:chars]
    payload = {"model":model,"messages":[{"role":"system","content":"You are a precise coding assistant."},{"role":"user","content":"Return one concise test name.\n"+body}],"max_tokens":128,"temperature":0,"stream":False,"chat_template_kwargs":{"enable_thinking":False}}
    start=time.perf_counter()
    try:
        req=urllib.request.Request(base.rstrip("/")+"/chat/completions", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r: result=json.loads(r.read())
        message=(result.get("choices") or [{}])[0].get("message") or {}; usage=result.get("usage") or {}
        return {"ok":bool(message.get("content")),"elapsed_s":round(time.perf_counter()-start,4),"prompt_tokens":usage.get("prompt_tokens"),"completion_tokens":usage.get("completion_tokens")}
    except Exception as e: return {"ok":False,"elapsed_s":round(time.perf_counter()-start,4),"error":f"{type(e).__name__}: {e}"}
def main():
    p=argparse.ArgumentParser(); p.add_argument("--base-url",default="http://127.0.0.1:8019/v1"); p.add_argument("--model",default="qwen3.8-flash-next-autoround"); p.add_argument("--sizes",default="4096,16384,32768"); p.add_argument("--timeout",type=float,default=900); p.add_argument("--output",type=Path); a=p.parse_args()
    rows=[post(a.base_url,a.model,int(size),a.timeout) | {"size_chars":int(size)} for size in a.sizes.split(",")]
    report={"schema":"flashnext-production-warmup-v1","model":a.model,"requests":rows,"ok":all(x["ok"] for x in rows)}
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report)); return 0 if report["ok"] else 1
if __name__ == "__main__": raise SystemExit(main())
