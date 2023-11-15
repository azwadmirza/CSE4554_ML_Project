    def _is_pdb_complete(self, source):
        """
        Check if the pdb input is ready to be executed.
        """
        if source and source[0] == '!':
            source = source[1:]
        if PY2:
            tm = IPythonInputSplitter()
        else:
            tm = TransformerManager()
        complete, indent = tm.check_complete(source)
        if indent is not None:
            indent = indent * ' '
        return complete != 'incomplete', indent