    def OnSelectUserResults(self, widget):

        if len(self.selected_users) == 0:
            return

        selected_user = widget.get_parent().user

        sel = self.ResultsList.get_selection()
        fmodel = self.ResultsList.get_model()
        sel.unselect_all()
        iter = self.resultsmodel.get_iter_first()

        self.UserRowIter(fmodel, sel, selected_user, iter)

        self.select_results()