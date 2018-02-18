# For backward compatibility
from .file.rec import Source as Base


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = self.name.replace('/', '_')
