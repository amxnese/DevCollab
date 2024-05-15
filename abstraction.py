from abc import ABC, abstractmethod

class Submitions(ABC):
    @abstractmethod
    def submit(self):
        pass

