    def reload(self):
        from pkg_resources import resource_filename
        cmdlist = TsvSheet('cmdlist', source=Path(resource_filename(__name__, 'commands.tsv')))
        options.set('delimiter', vd_system_sep, cmdlist)
        cmdlist.reload_sync()

        self.rows = []
        for (k, o), v in commands.iter(self.source):
            self.addRow(v)
            v.sheet = o

        self.cmddict = {}
        for cmdrow in cmdlist.rows:
            self.cmddict[(cmdrow.sheet, cmdrow.longname)] = cmdrow

        self.revbinds = {}  # [longname] -> keystrokes
        for (keystrokes, _), longname in bindkeys.iter(self.source):
            if keystrokes not in self.revbinds:
                self.revbinds[longname] = keystrokes