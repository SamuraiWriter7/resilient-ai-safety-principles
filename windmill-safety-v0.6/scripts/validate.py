"""Synthetic Windmill safety bridge conformance v0.6; no actual security guarantees."""
import json
from pathlib import Path
DATA=Path(__file__).resolve().parents[1]/"examples/v0.6/cases.json"
def validate(s):
    errors=[]
    if s["external_actor_control"]: errors.append("noninterference")
    if not s["core_healthy"] or s["common_failure"] or s["pressure"]>=95:
        if s["mode"]!="P":errors.append("mandatory_park")
    elif s["pressure"]>=85 or s["blade_failed"]:
        if s["mode"] not in ("N","P"):errors.append("mandatory_hold")
    if s["blade_failed"] and not s["blade_isolated"]:errors.append("isolation")
    if s["mode"] in ("N","P") and s["untrusted_ingress"]:errors.append("ingress")
    if s["mode"]=="P" and s["workers_running"]:errors.append("park_workers")
    if s["mode"]=="R" and s["untrusted_ingress"]:errors.append("offline_reverse")
    if s["swap_requested"] and not all(s[k] for k in ("old_lease_revoked","signature_verified","authority_verified","trace_verified","post_swap_verified","independent_reviewer")):errors.append("swap_gate")
    return errors
def main():
    doc=json.loads(DATA.read_text(encoding="utf-8"))
    assert doc["version"]=="0.6.0" and len(doc["cases"])>=20
    matched=0
    for c in doc["cases"]:
        state=dict(doc["defaults"],**c["changes"])
        failures=validate(state)
        actual="FAIL" if failures else "PASS"
        ok=actual==c["expected"]
        print(f"{'MATCH' if ok else 'MISMATCH'} {c['id']} expected={c['expected']} actual={actual} rules={','.join(failures) or '-'}")
        matched+=ok
    print(f"Matched {matched}/{len(doc['cases'])}")
    return int(matched!=len(doc["cases"]))
if __name__=="__main__":
    raise SystemExit(main())
