from attackdiff.asset import Asset
from attackdiff.storage import AssetStorage
from attackdiff.diff import diff_assets
from attackdiff.storage import SnapshotStorage
from attackdiff.cli import build_parser
from attackdiff.scanners.nmap import NmapScanner
from attackdiff.output import print_diff, diff_to_json
import os
import sys



def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
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

            sys.exit(0)

            
        
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

            sys.exit(0)


        
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

            sys.exit(0)


        elif args.command == "prune":
            storage = SnapshotStorage()

            print(args)
            print(storage.has_retention_rule(args))

            if (not storage.has_retention_rule(args)) and (not args.force):
                print("Refusing to prune without a retention rule.")
                print("Use at least one --keep-* option or add --force. Using --force without retention rule will delete the last 10 UNTAGGED snapshots")
                sys.exit(1)

            # Apply default retention policy ONLY if allowed
            if not storage.has_retention_rule(args):
                args.keep_last = 10

            if (args.force) and (not storage.has_retention_rule(args)):
                print("⚠️  WARNING: --force used without retention rules.")
                print("⚠️  This may delete ALL stored scans.")

            if args.force and args.dry_run:
                print("Dry-run active: no files will actually be deleted.")

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
                i = 0
                for d in result["decisions"]:
                    if d["action"] == "delete" :
                        i+=1
                print(f"Deleted {i} snapshots")

            sys.exit(0)
        
    except ValueError as e:
        print(f"[!] {e}")
        sys.exit(1)

    except Exception as e:
        print(f"[!] Runtime error: {e}")
        sys.exit(2)



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

attackdiff prune --keep-last 10 --keep-days 30

attackdiff prune --keep-last 10 --tag tag1 --dry-run



Exit code meaning : 
0 = Success
1 = User mistake / refused action
2 = Runtime / scanner failure
"""
