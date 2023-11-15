    def import_object(self) -> Any:
        ret = super().import_object()
        if inspect.isenumattribute(self.object):
            self.object = self.object.value
        if inspect.isattributedescriptor(self.object):
            self._datadescriptor = True
        else:
            # if it's not a data descriptor
            self._datadescriptor = False
        return ret