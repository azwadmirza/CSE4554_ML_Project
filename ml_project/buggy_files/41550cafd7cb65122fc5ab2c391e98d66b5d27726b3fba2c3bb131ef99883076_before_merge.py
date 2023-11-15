    def build_unit(self, unit):
        output = super().build_unit(unit)
        try:
            converted_source = xliff_string_to_rich(unit.get_source_plurals())
            converted_target = xliff_string_to_rich(unit.get_target_plurals())
        except XMLSyntaxError:
            return output
        output.rich_source = converted_source
        output.set_rich_target(converted_target, self.language.code)
        return output