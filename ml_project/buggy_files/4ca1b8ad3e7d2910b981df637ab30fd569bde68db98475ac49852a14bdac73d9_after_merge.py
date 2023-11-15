def get_figures(boxes, page_bbox, page_num, boxes_figures, page_width,
                page_height):

    # Filter out boxes with zero width or height
    filtered_boxes = []
    for bbox in boxes:
        if (bbox.x1 - bbox.x0 > 0 and bbox.y1 - bbox.y0 > 0):
            filtered_boxes.append(bbox)
    boxes = filtered_boxes

    if len(boxes) == 0:
        log.warning(
            "No boxes to get figures from on page {}.".format(page_num))
        return []

    plane = Plane(page_bbox)
    plane.extend(boxes)

    nodes_figures = []

    for fig_box in boxes_figures:
        node_fig = Node(fig_box)
        nodes_figures.append(node_fig)

    merge_indices = [i for i in range(len(nodes_figures))]
    page_stat = Node(boxes)
    nodes, merge_indices = merge_nodes(nodes_figures, plane, page_stat,
                                       merge_indices)

    ##Merging Nodes
    new_nodes = []
    for idx in range(len(merge_indices)):
        if (merge_indices[idx] == idx):
            new_nodes.append(nodes[idx])

    figures = [(page_num, page_width, page_height) +
               (node.y0, node.x0, node.y1, node.x1) for node in new_nodes]
    return figures