    def merge_domaindata(self, docnames, otherdata):
        # type: (List[unicode], Dict) -> None
        # print("merge_domaindata:")
        # print("self")
        # print(self.data['root_symbol'].dump(0))
        # print("other:")
        # print(otherdata['root_symbol'].dump(0))

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