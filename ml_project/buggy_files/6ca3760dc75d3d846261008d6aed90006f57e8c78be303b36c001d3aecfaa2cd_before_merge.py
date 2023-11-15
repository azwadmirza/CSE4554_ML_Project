    def magic_matches(self, text):
        """Match magics"""
        #print 'Completer->magic_matches:',text,'lb',self.text_until_cursor # dbg
        # Get all shell magics now rather than statically, so magics loaded at
        # runtime show up too.
        lsm = self.shell.magics_manager.lsmagic()
        line_magics = lsm['line']
        cell_magics = lsm['cell']
        pre = self.magic_escape
        pre2 = pre+pre
        
        # Completion logic:
        # - user gives %%: only do cell magics
        # - user gives %: do both line and cell magics
        # - no prefix: do both
        # In other words, line magics are skipped if the user gives %% explicitly
        bare_text = text.lstrip(pre)
        comp = [ pre2+m for m in cell_magics if m.startswith(bare_text)]
        if not text.startswith(pre2):
            comp += [ pre+m for m in line_magics if m.startswith(bare_text)]
        return comp