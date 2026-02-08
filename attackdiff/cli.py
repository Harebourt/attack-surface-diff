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
        choices=["nmap"],  # extensible later
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

        # ---- diff command ----
    diff_parser = subparsers.add_parser(
    "diff",
    help="Diff two attack surface snapshots"
    )

    group = diff_parser.add_mutually_exclusive_group(required=True)

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



    return parser
