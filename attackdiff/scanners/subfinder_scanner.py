import subprocess
from typing import Dict, List
from attackdiff.asset import Asset


class SubfinderScanner:
    """
    Runs Subfinder for a list of domains and returns discovered subdomains as Assets.
    """

    def __init__(self, extra_args: str = ""):
        self.extra_args = extra_args

    def scan(self, targets: List[str]) -> Dict[str, Asset]:
        if not isinstance(targets, list):
            raise TypeError("targets must be a list of domains")

        assets: Dict[str, Asset] = {}

        for target in targets:
            cmd = ["subfinder", "-d", target, "-silent"]

            if self.extra_args:
                import shlex
                cmd += shlex.split(self.extra_args)

            print("DEBUG subfinder cmd:", " ".join(cmd))

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[!] Warning: Subfinder failed for {target}: {result.stderr}")
                continue

            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue

                asset = Asset(
                    host=line,
                    ip=None,
                    ports=[],
                    services=[],
                    sources=["subfinder"]
                )
                assets[asset.id] = asset

        return assets
