    def __init__(self, module):
        super(VmAttributeDefManager, self).__init__(module)
        self.custom_field_mgr = self.content.customFieldsManager.field