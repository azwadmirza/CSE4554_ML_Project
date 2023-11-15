    def describe_stack_resource(self):
        stack_name = self._get_param("StackName")
        stack = self.cloudformation_backend.get_stack(stack_name)
        logical_resource_id = self._get_param("LogicalResourceId")

        for stack_resource in stack.stack_resources:
            if stack_resource.logical_resource_id == logical_resource_id:
                resource = stack_resource
                break

        template = self.response_template(DESCRIBE_STACK_RESOURCE_RESPONSE_TEMPLATE)
        return template.render(stack=stack, resource=resource)