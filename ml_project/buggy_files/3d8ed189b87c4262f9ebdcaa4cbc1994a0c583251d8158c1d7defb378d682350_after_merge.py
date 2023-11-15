    def show_syspath(self):
        """Show sys.path"""
        editor = CollectionsEditor(parent=self)
        editor.setup(sys.path, title="sys.path", readonly=True,
                     width=600, icon=ima.icon('syspath'))
        self.dialog_manager.show(editor)