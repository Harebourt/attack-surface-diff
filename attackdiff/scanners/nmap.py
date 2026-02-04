import subprocess
from typing import Dict, List
from asset import Asset
from scanners.scan import Scanner


class NmapScanner(Scanner):
    def __init__(self, extra_args: List[str] | None = None):
        self.extra_args = extra_args or []

    def scan(self, targets: List[str]) -> Dict[str, Asset]:
        """
        Scan one or more IPs using nmap and return Assets.
        """
        cmd = [
            "nmap",
            "-Pn",
            "-oG",
            "-",
            *self.extra_args,
            *targets
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Nmap scan failed: {e.stderr}")

        return self._parse_output(result.stdout)

    def _parse_output(self, output: str) -> Dict[str, Asset]:
        """
        Parse nmap grepable output and return assets keyed by IP.
        """
        assets: Dict[str, Asset] = {}

        for line in output.splitlines():
            if not line.startswith("Host:"):
                continue

            parts = line.split()
            ip = parts[1]

            if ip not in assets:
                assets[ip] = Asset(
                    host=ip,
                    ip=ip,
                    ports=[],
                    services=[],
                    sources=["nmap"]
                )

            if "Ports:" not in line:
                continue

            ports_part = line.split("Ports:")[1]
            entries = ports_part.split(",")

            for entry in entries:
                fields = entry.strip().split("/")
                if len(fields) < 5:
                    continue

                port = fields[0]
                state = fields[1]
                service = fields[4]

                if state != "open":
                    continue  # ignore filtered / open|filtered for now

                try:
                    port = int(port)
                except ValueError:
                    continue

                assets[ip].ports.append(port)

                if service and service != "?":
                    assets[ip].services.append(service)

        # Deduplicate
        for asset in assets.values():
            asset.ports = sorted(set(asset.ports))
            asset.services = sorted(set(asset.services))

        return assets
