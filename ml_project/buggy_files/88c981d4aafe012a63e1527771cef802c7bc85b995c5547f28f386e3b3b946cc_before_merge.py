def h5py_completer(self, event):
    """ Completer function to be loaded into IPython """
    base = re_object_match.split(event.line)[1]

    if not isinstance(self._ofind(base)['obj'], (AttributeManager, HLObject)):
        raise TryNext

    try:
        return h5py_attr_completer(self, event.line)
    except ValueError:
        pass

    try:
        return h5py_item_completer(self, event.line)
    except ValueError:
        pass

    return []