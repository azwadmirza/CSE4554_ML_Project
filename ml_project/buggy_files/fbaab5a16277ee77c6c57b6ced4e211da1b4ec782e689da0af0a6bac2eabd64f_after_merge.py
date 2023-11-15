def debugcell(cellname, filename=None, post_mortem=False):
    """Debug a cell."""
    if filename is None:
        filename = get_current_file_name()
        if filename is None:
            return

    debugger, filename = get_debugger(filename)
    # The breakpoint might not be in the cell
    debugger.continue_if_has_breakpoints = False
    debugger.run("runcell({}, {})".format(
        repr(cellname), repr(filename)))