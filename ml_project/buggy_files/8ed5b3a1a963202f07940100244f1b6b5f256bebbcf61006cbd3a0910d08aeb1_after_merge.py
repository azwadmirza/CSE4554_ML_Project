    def list_stack_resources(self):
        stack_name_or_id = self._get_param("StackName")
        resources = self.cloudformation_backend.list_stack_resources(stack_name_or_id)

        template = self.response_template(LIST_STACKS_RESOURCES_RESPONSE)
        return template.render(resources=resources)