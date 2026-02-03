import json
from pathlib import Path
from typing import Dict
from asset import Asset


class AssetStorage:
    def __init__(self, path: str):
        self.path = Path(path)
        self.assets: Dict[str, Asset] = {}

    def load(self):
        if not self.path.exists():
            self.assets = {}
            return

        if self.path.stat().st_size == 0:
            self.assets = {}
            return

        with open(self.path, "r") as f:
            raw = json.load(f)

        self.assets = {
            asset_id: Asset.from_dict(data)
            for asset_id, data in raw.items()
        }


    def save(self):
        """
        Save current snapshot to disk.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, "w") as f:
            json.dump(
                {aid: asset.to_dict() for aid, asset in self.assets.items()},
                f,
                indent=2
            )

    def upsert(self, new_asset: Asset):
        """
        Insert or update an asset based on its ID.
        """
        existing = self.assets.get(new_asset.id)

        if existing:
            # Preserve first_seen
            new_asset.first_seen = existing.first_seen
            # Update last_seen
            new_asset.last_seen = new_asset.last_seen
            self.assets[new_asset.id] = new_asset
        else:
            self.assets[new_asset.id] = new_asset
