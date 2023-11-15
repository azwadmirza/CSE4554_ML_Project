    def process(self, doctree: nodes.document, docname: str) -> None:
        todos = sum(self.domain.todos.values(), [])  # type: List[todo_node]
        for node in doctree.traverse(todolist):
            if not self.config.todo_include_todos:
                node.parent.remove(node)
                continue

            if node.get('ids'):
                content = [nodes.target()]  # type: List[Element]
            else:
                content = []

            for todo in todos:
                # Create a copy of the todo node
                new_todo = todo.deepcopy()
                new_todo['ids'].clear()

                # (Recursively) resolve references in the todo content
                self.env.resolve_references(new_todo, todo['docname'], self.builder)  # type: ignore  # NOQA
                content.append(new_todo)

                todo_ref = self.create_todo_reference(todo, docname)
                content.append(todo_ref)

            node.replace_self(content)