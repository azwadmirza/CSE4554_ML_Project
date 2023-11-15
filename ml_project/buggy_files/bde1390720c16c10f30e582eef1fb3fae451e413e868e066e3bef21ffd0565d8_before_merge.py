    def to_dict(self, view='collection', value_mapper=None, app=None):
        as_dict = super(ToolOutput, self).to_dict(view=view, value_mapper=value_mapper)
        format = self.format
        if format and format != "input" and app:
            edam_format = app.datatypes_registry.edam_formats.get(self.format)
            as_dict["edam_format"] = edam_format
            edam_data = app.datatypes_registry.edam_data.get(self.format)
            as_dict["edam_data"] = edam_data
        return as_dict