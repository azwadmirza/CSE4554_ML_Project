    def OnSelectUserResults(self, widget):

        if len(self.selected_users) == 0:
            return

        selected_user = widget.get_parent().user

        sel = self.ResultsList.get_selection()
        fmodel = self.ResultsList.get_model()
        sel.unselect_all()

        iter = fmodel.get_iter_first()

        SelectUserRowIter(fmodel, sel, 1, selected_user, iter)

        self.select_results()