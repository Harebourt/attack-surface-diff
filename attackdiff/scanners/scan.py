from abc import ABC, abstractmethod
from typing import Dict
from asset import Asset


class Scanner(ABC):
    @abstractmethod
    def scan(self, target: str) -> Dict[str, Asset]:
        """
        Run a scan against a target and return assets.
        Key = asset.id
        """
        pass
