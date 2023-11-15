    def add_generated_objects(node, generated_objects):
        # Do not add generated objects to project file. Those are automatically used by MSBuild, because
        # they are part of the CustomBuild Outputs.
        return