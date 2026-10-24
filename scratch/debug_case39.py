import csv
from code.identity import IdentityResolver
from code.state_reconstructor import StateReconstructor

recon = StateReconstructor("dataset")
with open("dataset/deletion_requests.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["case_id"] in ["case_39", "case_50"]:
            print(f"*** {row['case_id']} ***")
            prof = recon.resolver.resolve(row["email"])
            print("Profile:", prof)
            acts = recon.activity_loader.get_activities_in_window(row["requested_at"], row["audit_at"])
            print(f"Activities in window ({row['requested_at']} to {row['audit_at']}): {len(acts)}")
            for a in acts:
                if "user_14" in a.details or "aditi" in a.details.lower() or "jain" in a.details.lower():
                    print("  Act:", a.event_time, a.source_system, a.target_system, a.resource_id, a.event_type, a.details)
            obs = [o for o in recon.indexer.observations if o.captured_at <= row["audit_at"] and any(prof.matches(i) for i in o.identifiers)] if prof else []
            print(f"Matching obs: {len(obs)}")
            for o in obs:
                print("  Obs:", o.system_id, o.resource_id, o.status, o.file_id)
