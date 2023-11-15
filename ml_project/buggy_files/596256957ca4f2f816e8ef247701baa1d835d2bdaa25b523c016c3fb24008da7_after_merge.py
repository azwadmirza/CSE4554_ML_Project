def paged_object_to_list(paged_object):
    """
    Extract all pages within a paged object as a list of dictionaries
    """
    paged_return = []
    while True:
        try:
            page = next(paged_object)
            paged_return.append(page.as_dict())
        except StopIteration:
            break

    return paged_return