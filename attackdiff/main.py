from asset import Asset
from storage import AssetStorage
from diff import diff_assets
from storage import SnapshotStorage

"""
# Load previous snapshot
storage = AssetStorage("data/assets.json")
storage.load()
old_assets = storage.assets.copy()

# ----- Simulated scan results -----
current_assets = {}

a1 = Asset(
    host="1.2.3.4",
    ip="1.2.3.4",
    ports=[22],  # port 80 closed
    services=["ssh"],
    sources=["nmap"]
)

a2 = Asset(
    host="9.9.9.9",
    ip="9.9.9.9",
    ports=[443],
    services=["https"],
    sources=["nmap"]
)

current_assets[a1.id] = a1
current_assets[a2.id] = a2
# ---------------------------------

# Diff
diff = diff_assets(old_assets, current_assets)

print("\n=== DIFF ===")

print("\n[+] New assets:")
for a in diff["new_assets"]:
    print(" ", a.host)

print("\n[-] Missing assets:")
for a in diff["missing_assets"]:
    print(" ", a.host)

print("\n[*] Changed assets:")
for c in diff["changed_assets"]:
    print(
        f" {c['host']}\n New port : {c['ports_added']}\n Port removed :\
              {c['ports_removed']}\n New service : {c['services_added']}\
                \n Removed services : {c['services_removed']} \n \
                ###################################################"
    )

# Save new snapshot
storage.assets = current_assets
storage.save()
"""


storage = SnapshotStorage()
current_assets = {}

a1 = Asset(
    host="1.2.3.4",
    ip="1.2.3.4",
    ports=[22],  # port 80 closed
    services=["ssh"],
    sources=["nmap"]
)

a2 = Asset(
    host="9.9.9.9",
    ip="9.9.9.9",
    ports=[443],
    services=["https"],
    sources=["nmap"]
)

current_assets[a1.id] = a1
current_assets[a2.id] = a2

# current_assets = result of scan (dict[str, Asset])
snapshot_path = storage.save_snapshot(current_assets)

print(f"[+] Snapshot saved to {snapshot_path}")