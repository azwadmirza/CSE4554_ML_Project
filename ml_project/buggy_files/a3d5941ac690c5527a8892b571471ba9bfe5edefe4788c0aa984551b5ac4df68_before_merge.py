    def list_stack_resources(self, stack_name_or_id):
        stack = self.get_stack(stack_name_or_id)
        if stack is None:
            return None
        return stack.stack_resources