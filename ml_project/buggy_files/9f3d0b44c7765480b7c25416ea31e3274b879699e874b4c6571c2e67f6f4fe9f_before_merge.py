    def merge_domaindata(self, docnames, otherdata):
        # type: (List[unicode], Dict) -> None
        self.data['root_symbol'].merge_with(otherdata['root_symbol'],
                                            docnames, self.env)
        ourNames = self.data['names']
        for name, docname in otherdata['names'].items():
            if docname in docnames:
                if name in ourNames:
                    msg = "Duplicate declaration, also defined in '%s'.\n"
                    msg += "Name of declaration is '%s'."
                    msg = msg % (ourNames[name], name)
                    logger.warning(msg, docname)
                else:
                    ourNames[name] = docname