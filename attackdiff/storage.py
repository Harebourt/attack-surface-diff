import json
from pathlib import Path
from typing import Dict, List
from attackdiff.asset import Asset
from datetime import datetime, timezone, timedelta



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
    


    def find_snapshot_by_tag(self, tag: str) -> Path:
        """
        Return the most recent snapshot with the given tag
        """
        snapshots = self.list_snapshots()

        for path in reversed(snapshots):  # newest first
            meta = self.load_meta(path)
            if meta.get("tag") == tag:
                return path

        raise RuntimeError(f"No snapshot found with tag '{tag}'")
    

    def get_latest_snapshot(self) -> Path:
        snapshots = self.list_snapshots()
        if not snapshots:
            raise RuntimeError("No snapshots available")
        return snapshots[-1]
    

    def _parse_snapshot_meta(self, path: Path) -> dict:
        with open(path, "r") as f:
            raw = json.load(f)

        meta = raw.get("meta", {})

        timestamp = meta.get("timestamp")
        tag = meta.get("tag")

        created_at = datetime.fromisoformat(timestamp)

        return {
            "path": path,
            "created_at": created_at,
            "tag": tag
        }


    def list_snapshots_with_meta(self):
        snapshots = []

        for path in self.base_path.glob("*.json"):
            try:
                snapshots.append(self._parse_snapshot_meta(path))
            except Exception:
                # corrupted snapshot → skip
                continue

        return snapshots

    

    def prune(
        self,
        keep_last: int | None = None,
        keep_days: int | None = None,
        dry_run: bool = False,
        tag: str | None = None,
    ) -> dict:
        
        snapshots = self.list_snapshots_with_meta()
        now = datetime.now(timezone.utc)

        decisions = []
        keep = set()

        # -------------------------------
        # MODE 1: Scoped prune by tag
        # -------------------------------
        if tag:
            scoped = [s for s in snapshots if s["tag"] == tag]

            # Sort newest → oldest
            scoped.sort(key=lambda s: s["created_at"], reverse=True)

            # Keep last N
            for s in scoped[:keep_last]:
                keep.add(s["path"])
                decisions.append({
                    "path": s["path"],
                    "action": "keep",
                    "reason": f"keep-last (tag={tag})",
                    "tag": s["tag"],
                    "created_at": s["created_at"],
                })

            # Keep by age
            if keep_days is not None:
                cutoff = now - timedelta(days=keep_days)
                for s in scoped:
                    if s["created_at"] >= cutoff:
                        keep.add(s["path"])
                        decisions.append({
                            "path": s["path"],
                            "action": "keep",
                            "reason": f"within keep-days (tag={tag})",
                            "tag": s["tag"],
                            "created_at": s["created_at"],
                        })

            # Delete the rest
            for s in scoped:
                if s["path"] not in keep:
                    decisions.append({
                        "path": s["path"],
                        "action": "delete",
                        "reason": f"expired (tag={tag})",
                        "tag": s["tag"],
                        "created_at": s["created_at"],
                    })
                    if not dry_run:
                        s["path"].unlink(missing_ok=True)

            return {
                "dry_run": dry_run,
                "decisions": decisions
            }

        # -------------------------------
        # MODE 2: Global prune (no tag)
        # -------------------------------
        tagged = [s for s in snapshots if s["tag"]]
        untagged = [s for s in snapshots if not s["tag"]]

        # Keep all tagged forever
        for s in tagged:
            keep.add(s["path"])
            decisions.append({
                "path": s["path"],
                "action": "keep",
                "reason": f"tag={s['tag']}",
                "tag": s["tag"],
                "created_at": s["created_at"],
            })

        # Sort untagged newest → oldest
        untagged.sort(key=lambda s: s["created_at"], reverse=True)

        # Keep by age
        if keep_days is not None:
            cutoff = now - timedelta(days=keep_days)
            for s in untagged:
                if s["created_at"] >= cutoff:
                    keep.add(s["path"])
                    decisions.append({
                        "path": s["path"],
                        "action": "keep",
                        "reason": "within keep-days",
                        "tag": None,
                        "created_at": s["created_at"],
                    })

        # Keep last N untagged
        remaining = [s for s in untagged if s["path"] not in keep]
        for s in remaining[:keep_last]:
            keep.add(s["path"])
            decisions.append({
                "path": s["path"],
                "action": "keep",
                "reason": "keep-last",
                "tag": None,
                "created_at": s["created_at"],
            })

        # Delete the rest
        for s in untagged:
            if s["path"] not in keep:
                decisions.append({
                    "path": s["path"],
                    "action": "delete",
                    "reason": "expired",
                    "tag": None,
                    "created_at": s["created_at"],
                })
                if not dry_run:
                    s["path"].unlink(missing_ok=True)

        return {
            "dry_run": dry_run,
            "decisions": decisions
        }
    
    def has_retention_rule(self, args) -> bool:
        return any([
            args.keep_last is not None,
            args.keep_days is not None,
        ])






