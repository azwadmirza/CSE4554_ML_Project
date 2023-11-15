    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._add_scalars()
        self._create_service_field()
        self._extend_query_type()