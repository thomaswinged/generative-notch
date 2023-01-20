from attrs import define, field, Factory
from abc import ABC, abstractmethod


class PipelineModule(ABC):
    def set(self, item):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class PrioritySortedRegistry(PipelineModule):
    def register(self, item):
        pass