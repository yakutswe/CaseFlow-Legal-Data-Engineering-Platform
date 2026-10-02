from abc import ABC, abstractmethod
from typing import Any


class LegalSource(ABC):
    @abstractmethod
    def fetch(self) -> list[dict[str, Any]]:
        """
        Fetch raw legal records from a source.
        """
        raise NotImplementedError