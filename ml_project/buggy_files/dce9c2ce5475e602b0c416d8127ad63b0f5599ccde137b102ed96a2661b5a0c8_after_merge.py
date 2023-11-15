    def wrapcloseterm(self, widget):
        """A child terminal has closed, so this container must die"""
        dbg('Paned::wrapcloseterm: Called on %s' % widget)

        if self.closeterm(widget):
            # At this point we only have one child, which is the surviving term
            sibling = self.children[0]
            first_term_sibling = sibling
            cur_tabnum = None

            focus_sibling = True
            if self.get_toplevel().is_child_notebook():
                notebook = self.get_toplevel().get_children()[0]
                cur_tabnum = notebook.get_current_page()
                tabnum = notebook.page_num_descendant(self)
                nth_page = notebook.get_nth_page(tabnum)
                exiting_term_was_last_active = (notebook.last_active_term[nth_page] == widget.uuid)
                if exiting_term_was_last_active:
                    first_term_sibling = enumerate_descendants(self)[1][0]
                    notebook.set_last_active_term(first_term_sibling.uuid)
                    notebook.clean_last_active_term()
                    self.get_toplevel().last_active_term = None
                if cur_tabnum != tabnum:
                    focus_sibling = False
            elif self.get_toplevel().last_active_term != widget.uuid:
                focus_sibling = False

            self.remove(sibling)

            metadata = None
            parent = self.get_parent()
            metadata = parent.get_child_metadata(self)
            dbg('metadata obtained for %s: %s' % (self, metadata))
            parent.remove(self)
            self.cnxids.remove_all()
            parent.add(sibling, metadata)
            if cur_tabnum:
                notebook.set_current_page(cur_tabnum)
            if focus_sibling:
                first_term_sibling.grab_focus()
            elif not sibling.get_toplevel().is_child_notebook():
                try:
                    Terminator().find_terminal_by_uuid(sibling.get_toplevel().last_active_term.urn).grab_focus()
                except AttributeError:
                    dbg('cannot find terminal with uuid: %s' % sibling.get_toplevel().last_active_term.urn)
        else:
            dbg("Paned::wrapcloseterm: self.closeterm failed")