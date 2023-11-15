def get_view_name(namespace, view):
    """ create the name for the view
    """
    name = ""
    if namespace != "":
        name = namespace + "_"
    return name + view.name