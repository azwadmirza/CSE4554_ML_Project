    def iter_for_element(self, element, old_namespace=0):
        # Using `0` as sentinel
        if old_namespace != 0:
            parent_iter = self.iter_for_element(old_namespace)
        elif element and element.namespace:
            parent_iter = self.iter_for_element(element.namespace)
        else:
            parent_iter = None

        child_iter = self.model.iter_children(parent_iter)
        while child_iter:
            if self.model.get_value(child_iter, 0) is element:
                return child_iter
            child_iter = self.model.iter_next(child_iter)
        return None