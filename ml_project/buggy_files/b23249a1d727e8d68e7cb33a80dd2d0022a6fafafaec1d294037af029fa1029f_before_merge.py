def rorp_eq(src_rorp, dest_rorp):
    """Compare hardlinked for equality

    Return false if dest_rorp is linked differently, which can happen
    if dest is linked more than source, or if it is represented by a
    different inode.

    """
    if (not src_rorp.isreg() or not dest_rorp.isreg()
            or src_rorp.getnumlinks() == dest_rorp.getnumlinks() == 1):
        return 1  # Hard links don't apply

    if src_rorp.getnumlinks() < dest_rorp.getnumlinks():
        return 0
    src_key = get_inode_key(src_rorp)
    index, remaining, dest_key, digest = _inode_index[src_key]
    if dest_key == "NA":
        # Allow this to be ok for first comparison, but not any
        # subsequent ones
        _inode_index[src_key] = (index, remaining, None, None)
        return 1
    try:
        return dest_key == get_inode_key(dest_rorp)
    except KeyError:
        return 0  # Inode key might be missing if the metadata file is corrupt