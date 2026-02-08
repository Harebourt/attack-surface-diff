import json

def diff_to_json(diff: dict) -> str:
    """Function that outputs the diff in JSON format"""
    normalized = {
        "new_assets": {
            aid: asset.to_dict()
            for aid, asset in diff.get("new_assets", {}).items()
        },
        "missing_assets": {
            aid: asset.to_dict()
            for aid, asset in diff.get("missing_assets", {}).items()
        },
        "changed_assets": diff.get("changed_assets", [])
    }

    return json.dumps(normalized, indent=2)


def print_diff(diff: dict):
    """Function for CLI output of the diff"""
    new = diff.get("new_assets", {})
    removed = diff.get("missing_assets", {})
    changed = diff.get("changed_assets", {})

    if (
    not diff["new_assets"]
    and not diff["missing_assets"]
    and not diff["changed_assets"]
    ):
        print("[=] No changes detected")
        return


    if new:
        print("########################################################################\n")
        print("\n[+] New assets")
        for asset in new.values():
            print(f"  + {asset.host} \n \
        ports : {sorted(asset.ports)}\n \
        services : {sorted(asset.services)}")
        print("\n########################################################################")


    if removed:
        print("########################################################################\n")
        print("\n[-] Removed assets")
        for asset in removed.values():
            print(f"  - {asset.host} \n \
        ports : {sorted(asset.ports)}\n \
        services : {sorted(asset.services)}")
        print("\n########################################################################")


    if changed:
        print("########################################################################\n")
        print("\n[!] Changed assets")
        for i in changed :
            print(f"  ~ {i["host"]}")

            added_ports = i.get("ports_added", [])
            removed_ports = i.get("ports_removed", [])
            added_services = i.get("services_added", [])
            removed_services = i.get("services_removed", [])

            if added_ports :
                print(f"      + ports : {added_ports}")
            if added_services:
                print(f"      + services : {added_services}")

            print("\n")

            if removed_ports:
                print(f"      - ports : {removed_ports}")
            if removed_services:
                print(f"      - services : {removed_services}")
            
            print("\n")