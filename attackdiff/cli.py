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

    return parser
