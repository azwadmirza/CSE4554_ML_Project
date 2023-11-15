def item_at_line(root_item, line):
    """
    Find and return the item of the outline explorer under which is located
    the specified 'line' of the editor.
    """
    previous_item = root_item
    for item in get_item_children(root_item):
        if item.line > line:
            return previous_item
        previous_item = item
    else:
        return item