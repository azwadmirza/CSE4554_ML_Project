    def render_sphinx_doc(self, doc, context=None):
        """Transform doc string dictionary to HTML and show it"""
        # Math rendering option could have changed
        if self.main.editor is not None:
            fname = self.main.editor.get_current_filename()
            dname = osp.dirname(fname)
        else:
            dname = ''
        self._sphinx_thread.render(doc, context, self.get_option('math'),
                                   dname)