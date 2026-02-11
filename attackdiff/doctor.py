import sys
import shutil
from pathlib import Path
from attackdiff.storage import SnapshotStorage


REQUIRED_SCANNERS = [
    "nmap",
    "subfinder",
    "amass",
    "httpx",
]


def run_doctor() -> int:
    print("Running attackdiff doctor...\n")

    exit_code = 0

    # Python version
    print("Python version:")
    if sys.version_info >= (3, 10):
        print(f"  ✔ {sys.version.split()[0]}")
    else:
        print(f"  ✘ {sys.version.split()[0]} (Python 3.10+ required)")
        exit_code = 2

    # Data directory check
    print("\nData directory:")
    storage = SnapshotStorage()
    data_path = storage.base_path

    try:
        data_path.mkdir(parents=True, exist_ok=True)
        test_file = data_path / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        print(f"  ✔ Writable: {data_path}")
    except Exception as e:
        print(f"  ✘ Not writable: {data_path}")
        exit_code = 2

    # Snapshot integrity
    print("\nSnapshots:")
    snapshots = storage.list_snapshots()

    if not snapshots:
        print("  ⚠ No snapshots found")
        if exit_code == 0:
            exit_code = 1
    else:
        corrupted = False
        for snap in snapshots:
            try:
                storage.load_snapshot(snap)
            except Exception:
                corrupted = True
                print(f"  ✘ Corrupted snapshot: {snap.name}")
                exit_code = 2

        if not corrupted:
            print(f"  ✔ {len(snapshots)} snapshot(s) OK")

    # External scanners
    print("\nScanners:")
    for scanner in REQUIRED_SCANNERS:
        if shutil.which(scanner):
            print(f"  ✔ {scanner}")
        else:
            print(f"  ⚠ {scanner} not found")
            if exit_code == 0:
                exit_code = 1

    print("\nDoctor completed.")

    return exit_code
