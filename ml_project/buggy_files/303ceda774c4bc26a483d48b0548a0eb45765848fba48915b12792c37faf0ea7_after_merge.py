def extract_text_candidates(boxes, page_bbox, avg_font_pts, width, char_width,
                            page_num, ref_page_seen, boxes_figures, page_width,
                            page_height):
    #Too many "." in the Table of Content pages - ignore because it takes a lot of time
    if (len(boxes) == 0 or len(boxes) > 3500):
        return {}, False
    plane = Plane(page_bbox)
    plane.extend(boxes)

    #Row level clustering - identify objects that have same horizontal alignment
    rid2obj = [set([i]) for i in range(len(boxes))]  # initialize clusters
    obj2rid = list(range(
        len(boxes)))  # default object map to cluster with its own index
    prev_clusters = obj2rid
    while (True):
        for i1, b1 in enumerate(boxes):
            for i2, b2 in enumerate(boxes):
                if ((i1 == i2) or (obj2rid[i1] == obj2rid[i2])):
                    continue
                box1 = b1.bbox
                box2 = b2.bbox
                if ((abs(box1[1] - box2[1]) < 0.11 * avg_font_pts)
                        or ((abs(box1[3] - box2[3]) < 0.11 * avg_font_pts))
                        or (round((box1[1] + box1[3]) / 2) == round(
                            (box2[1] + box2[3]) / 2))):
                    min_i = min(i1, i2)
                    max_i = max(i1, i2)
                    rid1 = obj2rid[min_i]
                    rid2 = obj2rid[max_i]
                    for obj_iter in rid2obj[rid2]:
                        rid2obj[rid1].add(obj_iter)
                        obj2rid[obj_iter] = rid1
                    rid2obj[rid2] = set()
        if (prev_clusters == obj2rid):
            break
        prev_clusters = obj2rid

    cid2obj = [set([i]) for i in range(len(boxes))]  # initialize clusters
    obj2cid = list(range(
        len(boxes)))  # default object map to cluster with its own index
    prev_clusters = obj2cid

    #add the code for merging close text boxes in particular row
    while (True):
        for i1, b1 in enumerate(boxes):
            for i2, b2 in enumerate(boxes):
                if ((i1 == i2) or (obj2cid[i1] == obj2cid[i2])):
                    continue
                box1 = b1.bbox
                box2 = b2.bbox
                if (obj2rid[i1] == obj2rid[i2]):
                    if (((b1.bbox[0] < b2.bbox[0]) and
                         ((b2.bbox[0] - b1.bbox[2]) <= 2 * char_width)) or
                        ((b2.bbox[0] < b1.bbox[0]) and
                         ((b1.bbox[0] - b2.bbox[2]) <= 2 * char_width))):
                        min_i = min(i1, i2)
                        max_i = max(i1, i2)
                        cid1 = obj2cid[min_i]
                        cid2 = obj2cid[max_i]
                        for obj_iter in cid2obj[cid2]:
                            cid2obj[cid1].add(obj_iter)
                            obj2cid[obj_iter] = cid1
                        cid2obj[cid2] = set()
        if (prev_clusters == obj2cid):
            break
        prev_clusters = obj2cid

    #vertical alignment code
    while (True):
        for i1, b1 in enumerate(boxes):
            for i2, b2 in enumerate(boxes):
                if ((i1 == i2) or (obj2cid[i1] == obj2cid[i2])):
                    continue
                if (b1.bbox[1] < b2.bbox[1]):
                    box1 = b1.bbox
                    box2 = b2.bbox
                elif (b2.bbox[1] < b1.bbox[1]):
                    box1 = b2.bbox
                    box2 = b1.bbox
                else:
                    #horizontally aligned
                    continue
                if (abs((box2[3] - box2[1]) - (box1[3] - box1[1])) >
                        0.5 * avg_font_pts):
                    continue
                if (
                        box2[1] < box1[3]
                        or (box2[1] - box1[1] < 1.5 * avg_font_pts)
                        or (box2[3] - box1[3] < 1.5 * avg_font_pts)
                ):  #can probably do better if we find the average space between words
                    if (abs(box1[0] - box2[0]) < 3 * char_width
                            or abs(box1[2] - box2[2]) < 3 * char_width
                            or (((box1[0] + box1[2]) / 2) == (
                                (box2[0] + box2[2]) / 2))):
                        min_i = min(i1, i2)
                        max_i = max(i1, i2)
                        cid1 = obj2cid[min_i]
                        cid2 = obj2cid[max_i]
                        #move all objects from cluster cid2 to cid1
                        #reassign cluster ids for all such objects as well
                        for obj_iter in cid2obj[cid2]:
                            cid2obj[cid1].add(obj_iter)
                            obj2cid[obj_iter] = cid1
                        cid2obj[cid2] = set()
        if (prev_clusters == obj2cid):
            break
        prev_clusters = obj2cid

    #get cluster spans
    cid2span = {}
    for cid in range(len(cid2obj)):
        cid2span[cid] = {}
        cid2span[cid]["min_x"] = float("Inf")
        cid2span[cid]["min_y"] = float("Inf")
        cid2span[cid]["max_x"] = float("-Inf")
        cid2span[cid]["max_y"] = float("-Inf")
        for obj in cid2obj[cid]:
            cid2span[cid]["min_x"] = min(cid2span[cid]["min_x"],
                                         boxes[obj].bbox[0])
            cid2span[cid]["max_x"] = max(cid2span[cid]["max_x"],
                                         boxes[obj].bbox[2])
            cid2span[cid]["min_y"] = min(cid2span[cid]["min_y"],
                                         boxes[obj].bbox[1])
            cid2span[cid]["max_y"] = max(cid2span[cid]["max_y"],
                                         boxes[obj].bbox[3])

    #Don't split up references
    references_bbox = []
    references_cid = set()
    for cid in range(len(cid2obj)):
        if (len(cid2obj[cid]) == 1):
            if (boxes[list(
                    cid2obj[cid])[0]].get_text().lower() == "references"):
                references_bbox = [
                    cid2span[cid]["min_x"], cid2span[cid]["min_y"],
                    cid2span[cid]["max_x"], cid2span[cid]["max_y"]
                ]
                for cid2 in range(len(cid2obj)):
                    if (round(cid2span[cid]["min_x"]) == round(
                            cid2span[cid2]["min_x"]) and
                            cid2span[cid]["max_y"] < cid2span[cid2]["min_y"]):
                        references_cid.add(cid2)
                        cid2span[cid2]["min_x"] = cid2span[cid]["min_x"]
                        cid2span[cid2]["max_x"] = cid2span[cid]["max_x"]

    #get a list of empty cids
    empty_cids = [cid for cid in range(len(cid2obj)) if len(cid2obj[cid]) == 0]
    empty_idx = 0

    #Split paras based on whitespaces - seems to work
    if (ref_page_seen == False):
        for cid in range(len(cid2obj)):
            if (len(cid2obj[cid]) > 0 and cid not in empty_cids
                    and cid not in references_cid):
                cid_maxx = max([boxes[obj].bbox[2] for obj in cid2obj[cid]])
                cid_minx = min([boxes[obj].bbox[0] for obj in cid2obj[cid]])
                rid_list = set([obj2rid[obj] for obj in cid2obj[cid]])
                #Get min_y for each row
                rid_miny = {}
                for rid in rid_list:
                    rid_miny[rid] = min([
                        boxes[obj].bbox[1] if obj in cid2obj[cid] else 10000
                        for obj in rid2obj[rid]
                    ])
                sorted_rid_miny = sorted(
                    list(rid_miny.items()), key=operator.itemgetter(1))
                last_rid = 0
                for i in range(len(sorted_rid_miny) - 1):
                    row1 = sorted_rid_miny[i][0]
                    row2 = sorted_rid_miny[i + 1][0]
                    row1_maxx = max([
                        boxes[obj].bbox[2] if obj in cid2obj[cid] else -1
                        for obj in rid2obj[row1]
                    ])
                    row2_minx = min([
                        boxes[obj].bbox[0] if obj in cid2obj[cid] else 10000
                        for obj in rid2obj[row2]
                    ])
                    if (row1_maxx <= cid_maxx
                            and (row2_minx - char_width) > cid_minx):
                        #split cluster cid
                        new_cid_idx = empty_cids[empty_idx]
                        empty_idx += 1
                        for i_iter in range(last_rid, i + 1):
                            obj_list = [
                                obj
                                for obj in rid2obj[sorted_rid_miny[i_iter][0]]
                                if obj2cid[obj] == cid
                            ]
                            for obj in obj_list:
                                cid2obj[cid].remove(obj)
                                cid2obj[new_cid_idx].add(obj)
                                obj2cid[obj] = new_cid_idx
                        last_rid = i + 1

    clusters = [[boxes[i] for i in cluster]
                for cluster in filter(bool, cid2obj)]
    nodes = [Node(elems) for elems in clusters]
    node_indices = [i for i, x in enumerate(cid2obj) if x]
    merge_indices = [i for i in range(len(node_indices))]
    page_stat = Node(boxes)
    nodes, merge_indices = merge_nodes(nodes, plane, page_stat, merge_indices)

    ##Merging Nodes
    new_nodes = []
    new_node_indices = []
    for idx in range(len(merge_indices)):
        if (merge_indices[idx] == idx):
            new_nodes.append(nodes[idx])
            new_node_indices.append(node_indices[idx])

    #Heuristics for Node type
    ref_nodes = []
    new_ref_page_seen = False
    if (len(references_cid) > 0 or ref_page_seen or references_bbox != []):
        new_ref_page_seen = True
    ref_seen_in_node = False or ref_page_seen
    all_boxes = boxes + boxes_figures
    min_y_page = float("Inf")
    for idx, box in enumerate(all_boxes):
        min_y_page = min(min_y_page, box.bbox[1])
    if page_num == -1:
        #handle title, authors and abstract here
        log.error("TODO: no way to handle title authors abstract yet.")
    else:
        #eliminate header, footer, page number
        #sort other text and classify as header/paragraph
        new_nodes.sort(key=cmp_to_key(xy_reading_order))
        for idx, node in enumerate(new_nodes):
            if (idx < len(new_nodes) - 1):
                if ((round(node.y0) == round(min_y_page)
                     or math.floor(node.y0) == math.floor(min_y_page)) and
                        node.y1 - node.y0 < 2 * avg_font_pts):  #can be header
                    idx_new = idx + 1
                    if idx_new < len(new_nodes) - 1:
                        while (idx_new < len(new_nodes) - 1 and (
                            (round(node.y0) == round(new_nodes[idx_new].y0)) or
                            (math.floor(node.y0) == math.floor(
                                new_nodes[idx_new].y0)))):
                            idx_new += 1
                    if (idx_new < len(new_nodes) - 1):
                        if (new_nodes[idx_new].y0 - node.y0 >
                                1.5 * avg_font_pts):
                            node.type = "Header"
                            continue
            #get captions - first word is fig/figure/table
            first_elem = None
            for elem in node.elems:
                if (round(elem.bbox[0]) == round(node.x0)
                        and round(elem.bbox[1]) == round(node.y0)):
                    first_elem = elem
                    break
            if (first_elem != None):
                text = first_elem.get_text()
                if (len(text) > 10):
                    text = first_elem.get_text()[0:10]
                if ("Table" in text):
                    node.type = "Table Caption"
                    continue
                if ("Fig" in text or "Figure" in text):
                    node.type = "Figure Caption"
                    continue
                if (first_elem.get_text().lower() == "references"):
                    node.type = "Section Header"
                    ref_seen_in_node = True
                    continue
            if (ref_seen_in_node):
                node.type = "List"
                continue
            if (references_bbox != [] or ref_seen_in_node):
                if (node.y0 > references_bbox[3]
                        and node.x0 <= references_bbox[0]
                        and node.x1 > references_bbox[2]):
                    node.type = "List"
                    continue
            if (node.y1 - node.y0 <= 2.0 * avg_font_pts):  #one lines - section
                node.type = "Section Header"
            else:  #multiple lines - para
                node.type = "Paragraph"

    #handle references
    newer_nodes = []
    ref_indices = [False for idx in range(len(new_nodes))]
    for idx1, node1 in enumerate(new_nodes):
        if (ref_indices[idx1] == True):
            continue
        if (node1.type != "List"):
            newer_nodes.append(node1)
            continue
        x0, y0, x1, y1 = node1.x0, node1.y0, node1.x1, node1.y1
        newer_node = node1
        ref_indices[idx1] = True
        for idx2, node2 in enumerate(new_nodes):
            if (idx1 != idx2):
                if (node2.type == "List" and ref_indices[idx2] == False):
                    if ((node2.x0 <= x0 and node2.x1 >= x0)
                            or (x0 <= node2.x0 and x1 >= node2.x0)):
                        newer_node.merge(node2)
                        ref_indices[idx2] = True
        newer_nodes.append(newer_node)

    #handle figures
    for fig_box in boxes_figures:
        node_fig = Node(fig_box)
        node_fig.type = "Figure"
        newer_nodes.append(node_fig)

    tree = {}
    tree["section_header"] = [(page_num, page_width, page_height) +
                              (node.y0, node.x0, node.y1, node.x1)
                              for node in newer_nodes
                              if node.type == "Section Header"]
    tree["header"] = [(page_num, page_width, page_height) +
                      (node.y0, node.x0, node.y1, node.x1)
                      for node in newer_nodes if node.type == "Header"]
    tree["paragraph"] = [(page_num, page_width, page_height) +
                         (node.y0, node.x0, node.y1, node.x1)
                         for node in newer_nodes if node.type == "Paragraph"]
    # tree["figure"] = [(page_num, page_width, page_height) + (node.y0, node.x0, node.y1, node.x1) for node in newer_nodes if node.type=="Figure"]
    tree["figure_caption"] = [(page_num, page_width, page_height) +
                              (node.y0, node.x0, node.y1, node.x1)
                              for node in newer_nodes
                              if node.type == "Figure Caption"]
    tree["table_caption"] = [(page_num, page_width, page_height) +
                             (node.y0, node.x0, node.y1, node.x1)
                             for node in newer_nodes
                             if node.type == "Table Caption"]
    tree["list"] = [(page_num, page_width, page_height) +
                    (node.y0, node.x0, node.y1, node.x1)
                    for node in newer_nodes if node.type == "List"]
    return tree, new_ref_page_seen