    def _convert_sam_function_resource(name, resource_properties, layers):
        """
        Converts a AWS::Serverless::Function resource to a Function configuration usable by the provider.

        :param string name: LogicalID of the resource NOTE: This is *not* the function name because not all functions
            declare a name
        :param dict resource_properties: Properties of this resource
        :return samcli.commands.local.lib.provider.Function: Function configuration
        """

        codeuri = SamFunctionProvider._extract_sam_function_codeuri(name, resource_properties, "CodeUri")

        LOG.debug("Found Serverless function with name='%s' and CodeUri='%s'", name, codeuri)

        return Function(
            name=name,
            runtime=resource_properties.get("Runtime"),
            memory=resource_properties.get("MemorySize"),
            timeout=resource_properties.get("Timeout"),
            handler=resource_properties.get("Handler"),
            codeuri=codeuri,
            environment=resource_properties.get("Environment"),
            rolearn=resource_properties.get("Role"),
            layers=layers,
        )