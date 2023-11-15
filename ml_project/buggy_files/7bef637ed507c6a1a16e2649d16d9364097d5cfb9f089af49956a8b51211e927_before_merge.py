    def import_object(self) -> bool:
        """Never import anything."""
        # disguise as an attribute
        self.objtype = 'attribute'
        self.object = INSTANCEATTR
        self._datadescriptor = False
        return True