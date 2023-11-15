    def get_node_size(self, node):
        # User root node is bigger than normal nodes
        min_size = 0.01 if node[u'key'] != self.root_public_key else 0.05

        diff = abs(node.get('total_up', 0) - node.get('total_down', 0))
        if diff == 0:
            return min_size
        elif diff > 10 * TB:    # max token balance limit
            return 0.06  # max node size in graph
        elif diff > TB:
            return 0.05 + 0.005 * diff/TB  # 0.005 for each extra TB of balance
        return math.log(diff / (1024 * 1024), 2) / 512 + min_size