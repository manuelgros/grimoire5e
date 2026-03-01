from services.data_loader import DataLoader
from pathlib import Path

loader = DataLoader(Path("data"))
print(f"Loaded {len(loader.spells)} spells")
print(f"Loaded {len(loader.monsters)} monsters")
print(f"Loaded {len(loader.items)} items")
print(f"Loaded {len(loader.feats)} feats")
print(f"Loaded {len(loader.conditions)} conditions")