    def add_generated_objects(node, generated_objects):
        # Do not add generated objects to project file. Those are automatically used by MSBuild for VS2010, because
        # they are part of the CustomBuildStep Outputs.
        return