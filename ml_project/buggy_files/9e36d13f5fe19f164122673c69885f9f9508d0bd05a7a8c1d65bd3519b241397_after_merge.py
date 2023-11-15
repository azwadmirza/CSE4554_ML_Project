    def get_name(self, schema: s_schema.Schema) -> sn.QualName:
        component_ids = sorted(str(t.get_name(schema)) for t in self.types)
        nqname = f"({' | '.join(component_ids)})"
        return sn.QualName(name=nqname, module='__derived__')