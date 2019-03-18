# For backward compatibility
from denite.source.file.rec import Source as Base


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = self.name.replace('/', '_')

    def gather_candidates(self, context):
        self.error_message(context,
                           'Please use "file/rec" source instead.')
        return super().gather_candidates(context)
