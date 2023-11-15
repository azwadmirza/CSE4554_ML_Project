    def has_objects(objects, additional_objects, generated_objects):
        # Ignore generated objects, those are automatically used by MSBuild because they are part of
        # the CustomBuild Outputs.
        return len(objects) + len(additional_objects) > 0