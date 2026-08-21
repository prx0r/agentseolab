from dataclasses import dataclass, asdict
from typing import Optional, Any
import hashlib, json, uuid, datetime

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def canonical_hash(obj: Any) -> str:
    raw=json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

@dataclass
class SiteIntent:
    purpose: str
    primary_job: str
    audiences: list[str]
    capabilities: list[str]
    constraints: dict
    language: str = "en"
    metadata: dict | None = None

    def record(self):
        d=asdict(self)
        return {"intent_id": new_id("intent"), "intent_hash": canonical_hash(d),
                "created_at": now(), **d}
