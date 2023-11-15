    def _remove_element(self, root, element, remove_tail=False):
        parent = self._find_parent(root, element)
        if element.tail and not remove_tail:
            self._preserve_tail(element, parent)
        parent.remove(element)