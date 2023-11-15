def split_lines(nb):
    """split likely multiline text into lists of strings
    
    For file output more friendly to line-based VCS. ``rejoin_lines(nb)`` will
    reverse the effects of ``split_lines(nb)``.
    
    Used when writing JSON files.
    """
    for ws in nb.worksheets:
        for cell in ws.cells:
            if cell.cell_type == 'code':
                if 'input' in cell and isinstance(cell.input, basestring):
                    cell.input = cell.input.splitlines()
                for output in cell.outputs:
                    for key in _multiline_outputs:
                        item = output.get(key, None)
                        if isinstance(item, basestring):
                            output[key] = item.splitlines()
            else: # text, heading cell
                for key in ['source', 'rendered']:
                    item = cell.get(key, None)
                    if isinstance(item, basestring):
                        cell[key] = item.splitlines()
    return nb