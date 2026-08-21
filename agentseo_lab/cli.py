import argparse, json, sqlite3, uuid, datetime
from .db import connect
from .models import SiteIntent, new_id, now

def load(path):
    with open(path, encoding="utf-8") as f: return json.load(f)

def main():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="cmd", required=True)
    x=sp.add_parser("init-db"); x.add_argument("db")
    x=sp.add_parser("create-intent"); x.add_argument("db"); x.add_argument("json")
    x=sp.add_parser("create-experiment"); x.add_argument("db"); x.add_argument("json")
    x=sp.add_parser("ingest-observation"); x.add_argument("db"); x.add_argument("json")
    x=sp.add_parser("report"); x.add_argument("db")
    a=p.parse_args()
    db=connect(a.db)
    if a.cmd=="init-db":
        print(a.db)
    elif a.cmd=="create-intent":
        d=load(a.json); rec=SiteIntent(**d).record()
        db.execute("INSERT INTO intents VALUES(?,?,?,?)",
                   (rec["intent_id"],rec["intent_hash"],rec["created_at"],json.dumps(rec)))
        db.commit(); print(json.dumps(rec,indent=2))
    elif a.cmd=="create-experiment":
        d=load(a.json); eid=d.get("experiment_id",new_id("exp"))
        db.execute("INSERT INTO experiments VALUES(?,?,?,?,?,?,?)",
          (eid,d["intent_id"],now(),d["kind"],d.get("hypothesis_id"),
           int(d.get("preregistered",False)),json.dumps(d)))
        db.commit(); print(eid)
    elif a.cmd=="ingest-observation":
        d=load(a.json); oid=d.get("observation_id",new_id("obs"))
        db.execute("INSERT INTO observations VALUES(?,?,?,?,?,?,?,?,?,?,?)",
          (oid,d.get("experiment_id"),d["intent_id"],d.get("created_at",now()),
           d["evidence_tier"],d["event_type"],d.get("model_family"),
           d.get("model_version"),d.get("provider"),d.get("session_id"),json.dumps(d)))
        db.commit(); print(oid)
    elif a.cmd=="report":
        for table in ("intents","experiments","observations","candidates","domain_checks","outcomes","hypotheses"):
            print(table, db.execute(f"select count(*) from {table}").fetchone()[0])

if __name__=="__main__": main()
