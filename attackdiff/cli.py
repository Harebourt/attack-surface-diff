import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        prog="attackdiff",
        description="Attack surface diffing tool"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ---- scan command ----
    scan_parser = subparsers.add_parser(
        "scan",
        help="Run a scan and store a snapshot"
    )

    scan_parser.add_argument(
        "--scanner",
        required=True,
        choices=["nmap", "subfinder"],
        help="Scanner to use"
    )

    scan_parser.add_argument(
        "--targets",
        nargs="+",
        required=True,
        help="List of targets separated by a space (IP, domain)"
    )

    scan_parser.add_argument(
        "--nmap-args",
        default="",
        help="Extra arguments passed directly to nmap"
    )

    scan_parser.add_argument(
        "--tag",
        help="Optional tag for the scan (e.g. weekly, prod, baseline)"
    )

    scan_parser.add_argument(
        "--subfinder-args",
        default="",
        help="Extra arguments passed directly to subfinder"
    )

    scan_parser.add_argument(
        "--httpx",
        action="store_true",
        help="Run httpx on discovered domains (subfinder only)"
    )

    scan_parser.add_argument(
        "--httpx-args",
        default="",
        help="Extra arguments passed to httpx"
    )


        # ---- diff command ----
    diff_parser = subparsers.add_parser(
    "diff",
    help="Diff two attack surface snapshots"
    )

    group = diff_parser.add_mutually_exclusive_group()

    group.add_argument(
        "--last",
        action="store_true",
        help="Diff the last two snapshots"
    )

    group.add_argument(
        "--from",
        dest="from_snapshot",
        help="Older snapshot file (filename or path)"
    )

    diff_parser.add_argument(
        "--to",
        dest="to_snapshot",
        help="Newer snapshot file (filename or path)"
    )

    diff_parser.add_argument(
    "--json",
    action="store_true",
    help="Output diff as JSON"
    )

    diff_parser.add_argument(
    "--from-tag",
    help="Tag of the base snapshot"
    )

    diff_parser.add_argument(
        "--to-tag",
        help="Tag of the target snapshot"
    )

    diff_parser.add_argument(
    "--since",
    help="Diff from a tagged snapshot to the latest snapshot"
    )

    list_parser = subparsers.add_parser(
        "list",
        help="List available scan snapshots"
    )

    list_parser.add_argument(
        "--short",
        action="store_true",
        help="Only display snapshot filenames"
    )

    list_parser.add_argument(
    "--tag",
    help="Only list snapshots with this tag"
    )


    prune_parser = subparsers.add_parser(
    "prune",
    help="Delete old snapshots based on retention rules"
    )

    prune_parser.add_argument(
        "--keep-last",
        type=int,
        help="Number of most recent untagged snapshots to always keep (default: 10, use 0 to disable)"
    )

    prune_parser.add_argument(
        "--keep-days",
        type=int,
        help="Keep snapshots newer than N days"
    )

    prune_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting"
    )

    prune_parser.add_argument(
    "--tag",
    help="Only prune snapshots with this tag"
    )

    prune_parser.add_argument(
    "--force",
    action="store_true",
    help="Allow pruning without any retention rule (DANGEROUS)"
    )

    # ---- doctor command ----
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Check installation and environment health"
    )



    return parser
