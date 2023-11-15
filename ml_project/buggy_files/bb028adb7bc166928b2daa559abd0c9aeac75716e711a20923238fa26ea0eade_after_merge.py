    def get_displayname_static(cls, name: s_name.Name) -> str:
        if isinstance(name, s_name.QualName):
            return str(name)
        else:
            return s_name.unmangle_name(str(name))