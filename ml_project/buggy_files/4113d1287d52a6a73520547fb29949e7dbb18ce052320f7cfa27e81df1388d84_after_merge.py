    def __init__(self, match: str, scopes: List[Scope], **kwargs) -> None:

        for s in scopes:
            if s not in list(Scope):
                raise ValueError('invalid scope: {}'.format(s))

        self.id = kwargs.get('id', str(uuid4()))
        self.match = match
        self.scopes = scopes or list()