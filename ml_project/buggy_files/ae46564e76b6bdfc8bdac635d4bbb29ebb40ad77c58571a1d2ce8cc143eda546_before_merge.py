def get_order_args():
    """
        Get order arguments, return a dictionary
        { <VIEW_NAME>: (ORDER_COL, ORDER_DIRECTION) }

        Arguments are passed like: _oc_<VIEW_NAME>=<COL_NAME>&_od_<VIEW_NAME>='asc'|'desc'

    """
    orders = {}
    for arg in request.args:
        re_match = re.findall('_oc_(.*)', arg)
        if re_match:
            orders[re_match[0]] = (request.args.get(arg), request.args.get('_od_' + re_match[0]))
    return orders