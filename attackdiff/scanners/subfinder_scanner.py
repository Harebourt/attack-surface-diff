import subprocess
from typing import Dict, List
from attackdiff.asset import Asset
import shlex


class SubfinderScanner:
    """
    Runs Subfinder for a list of domains and returns discovered subdomains as Assets.
    """

    def __init__(
        self,
        extra_args: str = "",
        use_httpx: bool = False,
        httpx_args: str = ""
    ):
        self.extra_args = extra_args
        self.use_httpx = use_httpx
        self.httpx_args = httpx_args

    def scan(self, targets: list[str]) -> dict[str, Asset]:
        domains = self._run_subfinder(targets)

        if self.use_httpx:
            domains = self._run_httpx(domains)

        assets = {}
        for domain in domains:
            asset = Asset(
                host=domain,
                ports=[80, 443],  # assume HTTP layer
                services=["http"],
                sources=["subfinder"] + (["httpx"] if self.use_httpx else [])
            )
            assets[asset.id] = asset

        return assets
    
    
    
    def _run_subfinder(self, targets: list[str]) -> list[str]:
        cmd = ["subfinder", "-silent"]

        if self.extra_args:
            cmd += shlex.split(self.extra_args)

        for target in targets:
            cmd += ["-d", target]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        domains = list(set(result.stdout.strip().splitlines()))
        return domains
    


    def _run_httpx(self, domains: list[str]) -> list[str]:
        if not domains:
            return []

        cmd = ["httpx", "-silent"]

        if self.httpx_args:
            cmd += shlex.split(self.httpx_args)

        result = subprocess.run(
            cmd,
            input="\n".join(domains),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        alive = list(set(result.stdout.strip().splitlines()))
        return alive



