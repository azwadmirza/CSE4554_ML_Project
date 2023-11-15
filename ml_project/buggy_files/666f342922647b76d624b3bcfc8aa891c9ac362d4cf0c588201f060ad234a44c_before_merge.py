    def _post_exec_input(self, line):
        """Commands to be run after writing to stdin"""
        pdb_commands = ['next', 'continue', 'step', 'return']
        if any([x == line for x in pdb_commands]):
            # To open the file where the current pdb frame points to
            self.silent_exec_input("!get_ipython().kernel.get_pdb_step()")

            # To refresh the Variable Explorer
            self.silent_exec_input("!get_ipython().kernel.get_namespace_view()")
            self.silent_exec_input("!get_ipython().kernel.get_var_properties()")