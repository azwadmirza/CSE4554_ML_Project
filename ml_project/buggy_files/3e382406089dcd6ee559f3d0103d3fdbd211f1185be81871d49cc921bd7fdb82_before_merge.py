    def match(self, node):
        # type: (nodes.Node) -> bool
        try:
            if self.classes and not isinstance(node, self.classes):
                return False

            for key, value in self.attrs.items():
                if key not in node:
                    return False
                elif value is Any:
                    continue
                elif node.get(key) != value:
                    return False
            else:
                return True
        except Exception:
            # for non-Element nodes
            return False