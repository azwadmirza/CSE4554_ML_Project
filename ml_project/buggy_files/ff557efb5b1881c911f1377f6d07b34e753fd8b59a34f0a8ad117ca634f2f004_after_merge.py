    def get_module_members(self) -> Dict[str, ObjectMember]:
        """Get members of target module."""
        if self.analyzer:
            attr_docs = self.analyzer.attr_docs
        else:
            attr_docs = {}

        members = {}  # type: Dict[str, ObjectMember]
        for name in dir(self.object):
            try:
                value = safe_getattr(self.object, name, None)
                if ismock(value):
                    value = undecorate(value)
                docstring = attr_docs.get(('', name), [])
                members[name] = ObjectMember(name, value, docstring="\n".join(docstring))
            except AttributeError:
                continue

        # annotation only member (ex. attr: int)
        try:
            for name in inspect.getannotations(self.object):
                if name not in members:
                    docstring = attr_docs.get(('', name), [])
                    members[name] = ObjectMember(name, INSTANCEATTR,
                                                 docstring="\n".join(docstring))
        except AttributeError:
            pass

        return members