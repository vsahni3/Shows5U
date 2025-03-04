from abc import ABC, abstractmethod
class Validator(ABC):
    """Abstract base class for validation logic."""

    @abstractmethod
    def validate(self, data):
        """Abstract method that must be implemented by subclasses."""
        pass


        