    def process_doc(self, env, docname, document):
        # type: (BuildEnvironment, unicode, nodes.Node) -> None
        if Symbol.debug_show_tree:
            print("process_doc:", docname)
            print(self.data['root_symbol'].dump(0))
            print("process_doc end:", docname)