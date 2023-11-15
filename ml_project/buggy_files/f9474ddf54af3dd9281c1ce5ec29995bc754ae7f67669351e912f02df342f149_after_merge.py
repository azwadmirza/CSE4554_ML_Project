    def merge_domaindata(self, docnames, otherdata):
        # type: (List[unicode], Dict) -> None
        if Symbol.debug_show_tree:
            print("merge_domaindata:")
            print("\tself:")
            print(self.data['root_symbol'].dump(1))
            print("\tself end")
            print("\tother:")
            print(otherdata['root_symbol'].dump(1))
            print("\tother end")
            print("merge_domaindata end")

        self.data['root_symbol'].merge_with(otherdata['root_symbol'],
                                            docnames, self.env)
        ourNames = self.data['names']
        for name, docname in otherdata['names'].items():
            if docname in docnames:
                if name in ourNames:
                    msg = __("Duplicate declaration, also defined in '%s'.\n"
                             "Name of declaration is '%s'.")
                    msg = msg % (ourNames[name], name)
                    logger.warning(msg, location=docname)
                else:
                    ourNames[name] = docname