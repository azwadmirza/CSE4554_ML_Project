    def __init__(self,
                 router: Router,
                 endpoint_name,
                 handle_options: Optional[HandleOptions] = None):
        self.router = router
        self.endpoint_name = endpoint_name
        self.handle_options = handle_options or HandleOptions()