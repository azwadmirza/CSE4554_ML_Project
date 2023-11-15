    def _fetch_children(self) -> None:
        self._last_child_refresh = datetime.now()
        for page in self.client.get_paginator("describe_stacks").paginate():
            for stack in page["Stacks"]:
                if self._children.filter(id=stack["StackId"]):
                    continue
                if "ParentId" in stack.keys():
                    if self.id == stack["ParentId"]:
                        stack_obj = Stack._import_child(stack, self)
                        self._children.append(stack_obj)