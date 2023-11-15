    def __init__(self, match: str, scopes: List[Scope], **kwargs) -> None:

        self.id = kwargs.get('id', str(uuid4()))
        self.match = match
        self.scopes = scopes or list()