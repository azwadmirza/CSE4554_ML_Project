    def full_closure(self, node):
        # Needed to propagate correctly the cpp_info even with privates
        closure = OrderedDict()
        current = node.neighbors()
        while current:
            new_current = []
            for n in current:
                closure[n] = n
            for n in current:
                for neigh in n.public_neighbors():
                    if neigh not in new_current and neigh not in closure:
                        new_current.append(neigh)
            current = new_current
        return closure