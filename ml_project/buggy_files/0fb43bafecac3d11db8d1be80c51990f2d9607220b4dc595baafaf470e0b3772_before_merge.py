def merge_adjacent_blocks(blocks):
    cfg = compute_cfg_from_blocks(blocks)
    # merge adjacent blocks
    removed = set()
    for label in list(blocks.keys()):
        if label in removed:
            continue
        block = blocks[label]
        succs = list(cfg.successors(label))
        while True:
            if len(succs) != 1:
                break
            next_label = succs[0][0]
            if next_label in removed:
                break
            preds = list(cfg.predecessors(next_label))
            succs = list(cfg.successors(next_label))
            if len(preds) != 1 or preds[0][0] != label:
                break
            next_block = blocks[next_label]
            # XXX: commented out since scope objects are not consistent
            # thoughout the compiler. for example, pieces of code are compiled
            # and inlined on the fly without proper scope merge.
            # if block.scope != next_block.scope:
            #     break
            # merge
            block.body.pop()  # remove Jump
            block.body += next_block.body
            del blocks[next_label]
            removed.add(next_label)
            label = next_label