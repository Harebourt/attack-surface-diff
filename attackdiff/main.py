from attackdiff.asset import Asset
from attackdiff.storage import AssetStorage
from attackdiff.diff import diff_assets
from attackdiff.storage import SnapshotStorage
from attackdiff.cli import build_parser
from attackdiff.scanners.nmap import NmapScanner
from attackdiff.output import print_diff, diff_to_json
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

        snapshot_path = storage.save_snapshot(
            assets,
            tag=args.tag,
            scanner=args.scanner
        )

        print(f"[+] Scan saved: {snapshot_path.name}")

        print(f"[+] Scan completed: {snapshot_path}")

        
    
    elif args.command == "diff":
        storage = SnapshotStorage()

        # ---- Mode 1: last ----
        if args.last:
            if args.from_snapshot or args.to_snapshot or args.from_tag or args.to_tag:
                raise SystemExit("[!] --last cannot be combined with other diff options")

            old_assets, new_assets = storage.load_last_two_snapshots()

        # ---- Mode 2: explicit snapshots ----
        elif args.from_snapshot or args.to_snapshot:

            if args.from_tag or args.to_tag:
                raise SystemExit("[!] --from/--to cannot be combined with tags")
            
            if not (args.from_snapshot and args.to_snapshot):
                raise SystemExit("[!] --from requires --to")

            old_path = storage.resolve_snapshot(args.from_snapshot)
            new_path = storage.resolve_snapshot(args.to_snapshot)

            old_assets = storage.load_snapshot(old_path)
            new_assets = storage.load_snapshot(new_path)

        # ---- Mode 3: tags ----
        elif args.from_tag or args.to_tag:
            if not (args.from_tag and args.to_tag):
                raise SystemExit("[!] --from-tag requires --to-tag")

            from_path = storage.find_snapshot_by_tag(args.from_tag)
            to_path = storage.find_snapshot_by_tag(args.to_tag)

            old_assets = storage.load_snapshot(from_path)
            new_assets = storage.load_snapshot(to_path)

        # ---- Mode 4: since ----
        elif args.since:
            base_path = storage.find_snapshot_by_tag(args.since)
            latest_path = storage.get_latest_snapshot()

            old_assets = storage.load_snapshot(base_path)
            new_assets = storage.load_snapshot(latest_path)

        else:
            raise SystemExit(
                "[!] You must specify one diff mode: "
                "--last OR --from/--to OR --from-tag/--to-tag OR --since"
            )
        

        diff = diff_assets(old_assets, new_assets)

        if args.json:
            from attackdiff.output import diff_to_json
            print(diff_to_json(diff))
        else:
            print_diff(diff)


    
    elif args.command == "list":
        storage = SnapshotStorage()
        snapshots = storage.list_snapshots()

        if not snapshots:
            print("[!] No snapshots found")
            return

        for path in snapshots:
            meta = storage.load_meta(path)
            tag = meta.get("tag", "-")

            if args.short:
                if args.tag and meta.get("tag") != args.tag:
                    continue
                print(path.name)

            else:
                if args.tag and meta.get("tag") != args.tag:
                    continue

                assets = storage.load_snapshot(path)

                print(f"{path.name:<30} tag: {tag} assets: {len(assets)}")


    elif args.command == "prune":
        storage = SnapshotStorage()

        result = storage.prune(
            keep_last=args.keep_last,
            keep_days=args.keep_days,
            dry_run=args.dry_run,
            tag=args.tag
        )

        if args.dry_run:
            for d in result["decisions"]:
                label = "[KEEP]" if d["action"] == "keep" else "[DELETE]"
                print(
                    f"{label:<8} {d['path'].name} "
                    f"(reason: {d['reason']})"
                )
        else:
            print(f"Deleted {result['deleted']} snapshots")



"""
Example commands :

attackdiff scan --scanner nmap --targets 1.1.1.1 1.1.1.2 --nmap-arg="-sS -p80"

attackdiff diff --from file1.json --to file2.json

attackdiff diff --last

attackdiff diff --from-tag tag1 --to-tag tag2

attackdiff diff --since tag1 --json

attackdiff list --short

attackdiff list 

attackdiff list --tag tag1
"""
