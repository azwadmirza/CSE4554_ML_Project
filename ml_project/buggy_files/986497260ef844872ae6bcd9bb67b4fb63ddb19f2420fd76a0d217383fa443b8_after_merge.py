    def process(self, doctree: nodes.document, docname: str) -> None:
        todos = sum(self.domain.todos.values(), [])  # type: List[todo_node]
        document = new_document('')
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
                #
                # Note: To resolve references, it is needed to wrap it with document node
                document += new_todo
                self.env.resolve_references(document, todo['docname'], self.builder)
                document.remove(new_todo)
                content.append(new_todo)

                todo_ref = self.create_todo_reference(todo, docname)
                content.append(todo_ref)

            node.replace_self(content)