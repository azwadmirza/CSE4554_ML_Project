def sorted_allowed_list(allowed_list):
    """Sort allowed_list (output of format_allowed) by protocol and port."""
    # sort by protocol
    allowed_by_protocol = sorted(allowed_list,key=lambda x: x['IPProtocol'])
    # sort the ports list
    return sorted(allowed_by_protocol, key=lambda y: y.get('ports', []).sort())