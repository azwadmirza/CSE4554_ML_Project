    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super(ApplicationForm, self).__init__(*args, **kwargs)
        for field in self.application.system_app_type.enforced_data:
            # preserve existing value for disabled fields
            self[field].data = self[field].object_data