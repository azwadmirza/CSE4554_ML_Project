    def clear_doc(self, docname):
        # type: (unicode) -> None
        if Symbol.debug_show_tree:
            print("clear_doc:", docname)
            print("\tbefore:")
            print(self.data['root_symbol'].dump(1))
            print("\tbefore end")

        rootSymbol = self.data['root_symbol']
        rootSymbol.clear_doc(docname)

        if Symbol.debug_show_tree:
            print("\tafter:")
            print(self.data['root_symbol'].dump(1))
            print("\tafter end")
            print("clear_doc end:", docname)
        for name, nDocname in list(self.data['names'].items()):
            if nDocname == docname:
                del self.data['names'][name]