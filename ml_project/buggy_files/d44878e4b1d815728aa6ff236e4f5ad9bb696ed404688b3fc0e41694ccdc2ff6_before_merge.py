    def has_objects(objects, additional_objects, generated_objects):
        # Ignore generated objects, those are automatically used by MSBuild for VS2010, because they are part of
        # the CustomBuildStep Outputs.
        return len(objects) + len(additional_objects) > 0