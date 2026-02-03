from asset import Asset
from storage import AssetStorage

storage = AssetStorage("data/assets.json")
storage.load()

asset = Asset(
    host="1.2.3.4",
    ip="1.2.3.4",
    ports=[22, 80],
    services=["ssh", "http"],
    sources=["nmap"]
)

storage.upsert(asset)
storage.save()

print("Assets saved:", len(storage.assets))
