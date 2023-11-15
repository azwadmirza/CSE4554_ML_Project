    def get_edge_label(edge):
        node_service = monkey_island.cc.services.node.NodeService
        from_id = edge["from"]
        to_id = edge["to"]

        from_label = Monkey.get_label_by_id(from_id)

        if to_id == ObjectId("000000000000000000000000"):
            to_label = 'MonkeyIsland'
        else:
            if Monkey.is_monkey(to_id):
                to_label = Monkey.get_label_by_id(to_id)
            else:
                to_label = node_service.get_node_label(node_service.get_node_by_id(to_id))

        return "%s %s %s" % (from_label, RIGHT_ARROW, to_label)