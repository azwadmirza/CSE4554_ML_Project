    def __init__(self, content_type=None, **kwargs):
        super(AdminPageChooser, self).__init__(**kwargs)

        self.target_content_types = content_type or ContentType.objects.get_for_model(Page)
        # Make sure target_content_types is a list or tuple
        if not isinstance(self.target_content_types, (list, tuple)):
            self.target_content_types = [self.target_content_types]