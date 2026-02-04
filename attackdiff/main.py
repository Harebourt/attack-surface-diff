from attackdiff.asset import Asset
from attackdiff.storage import AssetStorage
from attackdiff.diff import diff_assets
from attackdiff.storage import SnapshotStorage

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



"""
"""

# --- Simulate scan result ---
current_assets = {
    "1.2.3.4": Asset(host="1.2.3.4", ip="1.2.3.4", ports=[22,80], services=["ssh", "http"], sources=["nmap"]),
    "9.9.9.8": Asset(host="9.9.9.8", ip="9.9.9.8", ports=[443], services=["https"], sources=["nmap"])
}

# --- Save snapshot ---
storage = SnapshotStorage()
snapshot_path = storage.save_snapshot(current_assets)
print(f"[+] Snapshot saved to {snapshot_path}")

# --- Load last two snapshots ---
try:
    old_assets, new_assets = storage.load_last_two_snapshots()
except RuntimeError:
    print("Not enough snapshots to diff")
    old_assets, new_assets = {}, current_assets

# --- Compute diff ---
diff = diff_assets(old_assets, new_assets)

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
        f" {c['host']}\n New port : {c['ports_added']}\n Port removed : \
            {c['ports_removed']}\n New service : {c['services_added']}\
                \n Removed services : {c['services_removed']} \n \
############################################################################################"
    )

"""

from attackdiff.cli import build_parser
from attackdiff.scanners.nmap import NmapScanner
import os


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        # Targets are already a list thanks to nargs="+"
        targets = args.targets

        if args.scanner == "nmap":
            # Warn about privileged scan options
            if args.nmap_args and os.name != "nt":
                if os.geteuid() != 0:
                    print("[!] Warning: some Nmap options may require sudo")

            scanner = NmapScanner(
                extra_args=args.nmap_args
            )
        else:
            raise ValueError(f"Unknown scanner: {args.scanner}")

        # Run scan
        assets = scanner.scan(targets=targets)

        # Store snapshot
        storage = SnapshotStorage()
        snapshot_path = storage.save_snapshot(assets)

        print(f"[+] Scan completed: {snapshot_path}")

