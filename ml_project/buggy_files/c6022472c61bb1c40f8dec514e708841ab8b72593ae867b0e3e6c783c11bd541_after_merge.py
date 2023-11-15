    def _on_element_delete(self, event):
        element = event.element
        if type(element) in self.filter:
            iter = self.iter_for_element(element)
            # iter should be here, unless we try to delete an element who's
            # parent element is already deleted, so let's be lenient.
            if iter:
                self.model.remove(iter)