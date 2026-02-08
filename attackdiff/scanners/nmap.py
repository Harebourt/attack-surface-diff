import subprocess
import shlex
import xml.etree.ElementTree as ET
from attackdiff.asset import Asset


class NmapScanner:
    def __init__(self, extra_args: str = ""):
        self.extra_args = extra_args

    def scan(self, targets: list[str]) -> dict[str, Asset]:
        if not isinstance(targets, list):
            raise TypeError("targets must be a list")

        cmd = ["nmap", "-Pn"]

        if self.extra_args:
            cmd += shlex.split(self.extra_args)

        cmd += ["-oX", "-"]
        cmd += targets

        print("DEBUG nmap cmd:", " ".join(cmd))

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return self._parse_xml(result.stdout)

    def _parse_xml(self, xml_data: str) -> dict[str, Asset]:
        root = ET.fromstring(xml_data)
        assets = {}

        for host in root.findall("host"):
            status = host.find("status").attrib.get("state")
            addr = host.find("address").attrib.get("addr")
            print("DEBUG host:", addr, "status:", status)
            if status != "up":
                continue

            ip = None
            for addr in host.findall("address"):
                if addr.attrib.get("addrtype") in ("ipv4", "ipv6"):
                    ip = addr.attrib.get("addr")
                    break

            if ip is None:
                continue  # no usable IP, skip host


            ports = []
            services = []

            ports_el = host.find("ports")
            if ports_el is not None:
                for port in ports_el.findall("port"):
                    state = port.find("state").attrib.get("state")
                    if state not in ("open", "open|filtered"):
                        continue

                    portid = int(port.attrib["portid"])
                    ports.append(portid)

                    service = port.find("service")
                    if service is not None:
                        services.append(service.attrib.get("name"))

            asset = Asset(
                host=ip,
                ip=ip,
                ports=ports,
                services=services,
                sources=["nmap"]
            )


            assets[asset.id] = asset

        return assets
