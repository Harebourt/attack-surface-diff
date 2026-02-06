from typing import Dict, List
from attackdiff.asset import Asset


def diff_assets(
    old_assets: Dict[str, Asset],
    new_assets: Dict[str, Asset]
) -> dict:

    old_ids = set(old_assets.keys())
    new_ids = set(new_assets.keys())

    # Asset-level diffs
    new_asset_ids = new_ids - old_ids
    missing_asset_ids = old_ids - new_ids
    common_asset_ids = old_ids & new_ids

    new_assets_dict = {aid: new_assets[aid] for aid in new_asset_ids}
    missing_assets_dict = {aid: old_assets[aid] for aid in missing_asset_ids}

    # State-level diffs
    changed_assets = []

    for aid in common_asset_ids:
        old = old_assets[aid]
        new = new_assets[aid]

        old_ports = set(old.ports)
        new_ports = set(new.ports)

        ports_added = sorted(new_ports - old_ports)
        ports_removed = sorted(old_ports - new_ports)

        old_services = set(old.services)
        new_services = set(new.services)

        services_added = sorted(new_services - old_services)
        services_removed = sorted(old_services - new_services)

        if ports_added or ports_removed or services_added or services_removed:
            changed_assets.append({
                "host": new.host,
                "ports_added": ports_added,
                "ports_removed": ports_removed,
                "services_added": services_added,
                "services_removed": services_removed
            })

    return {
        "new_assets": new_assets_dict,
        "missing_assets": missing_assets_dict,
        "changed_assets": changed_assets
    }
