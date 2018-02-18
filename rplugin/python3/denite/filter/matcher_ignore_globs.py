# For backward compatibility
from .matcher.ignore_globs import Filter as Base


class Filter(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = self.name.replace('/', '_')
