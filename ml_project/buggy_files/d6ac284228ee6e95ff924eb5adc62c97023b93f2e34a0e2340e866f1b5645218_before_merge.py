    def _preserve_tail(self, element, parent):
        index = list(parent).index(element)
        if index == 0:
            parent.text = (parent.text or '') + element.tail
        else:
            sibling = parent[index-1]
            sibling.tail = (sibling.tail or '') + element.tail