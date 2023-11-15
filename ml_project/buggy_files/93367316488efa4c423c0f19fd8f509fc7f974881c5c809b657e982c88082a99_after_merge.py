    def full_closure(self, node, private=False):
        # Needed to propagate correctly the cpp_info even with privates
        closure = OrderedDict()
        current = node.neighbors()
        while current:
            new_current = []
            for n in current:
                closure[n] = n
            for n in current:
                neighbors = n.public_neighbors() if not private else n.neighbors()
                for neigh in neighbors:
                    if neigh not in new_current and neigh not in closure:
                        new_current.append(neigh)
            current = new_current
        return closure