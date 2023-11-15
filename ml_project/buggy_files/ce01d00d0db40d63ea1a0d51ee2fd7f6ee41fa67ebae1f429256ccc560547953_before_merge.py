    def get_weight(self):
        """ Return "weight" of a process and all its children for sorting. """
        if self.sort_key == "name":
            return self.stats[self.sort_key]

        # sum ressource usage for self and children
        total = 0
        nodes_to_sum = collections.deque([self])
        while nodes_to_sum:
            current_node = nodes_to_sum.pop()
            if callable(self.sort_key):
                total += self.sort_key(current_node.stats)
            elif self.sort_key == "io_counters":
                stats = current_node.stats[self.sort_key]
                total += stats[0] - stats[2] + stats[1] - stats[3]
            else:
                total += current_node.stats[self.sort_key]
            nodes_to_sum.extend(current_node.children)

        return total