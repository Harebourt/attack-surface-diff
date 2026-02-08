import json
from pathlib import Path
from typing import Dict, List
from attackdiff.asset import Asset
from datetime import datetime, timezone



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


class SnapshotStorage:
    def __init__(self, base_path: str = "data/scans"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_snapshot(
        self,
        assets: Dict[str, Asset],
        tag: str | None = None,
        scanner: str | None = None
    ) -> Path:
        timestamp = datetime.now(timezone.utc).isoformat()

        snapshot = {
            "meta": {
                "timestamp": timestamp,
                "tag": tag,
                "scanner": scanner
            },
            "assets": {
                asset_id: asset.to_dict()
                for asset_id, asset in assets.items()
            }
        }

        filename = timestamp.replace(":", "-") + ".json"
        path = self.base_path / filename

        with open(path, "w") as f:
            json.dump(snapshot, f, indent=2)

        return path
    


    def resolve_snapshot(self, value: str) -> Path:
        path = Path(value)

        if path.exists():
            return path

        candidate = self.base_path / value
        if candidate.exists():
            return candidate

        raise FileNotFoundError(f"Snapshot not found: {value}")



    def list_snapshots(self) -> List[Path]:
        """
        Return a sorted list of all snapshot files (oldest → newest)
        """
        files = sorted(self.base_path.glob("*.json"))
        return files


    def load_snapshot(self, path: Path) -> Dict[str, Asset]:
        """
        Load a snapshot JSON into Asset objects
        """
        with open(path, "r") as f:
            raw = json.load(f)

        assets_raw = raw.get("assets", {})

        return {aid: Asset.from_dict(data) for aid, data in assets_raw.items()}


    def load_meta(self, path: Path) -> dict:
        with open(path, "r") as f:
            raw = json.load(f)
        return raw.get("meta", {})


    def load_last_two_snapshots(self):
        """
        Load the last two snapshots for diffing
        """
        snapshots = self.list_snapshots()
        if len(snapshots) < 2:
            raise RuntimeError("Not enough snapshots to diff")
        return self.load_snapshot(snapshots[-2]), self.load_snapshot(snapshots[-1])