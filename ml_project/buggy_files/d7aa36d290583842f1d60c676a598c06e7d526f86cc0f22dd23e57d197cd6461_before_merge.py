def __need_to_keep__(name):
    if name in ['StaticInput', 'LayerType', 'layer_support']:
        return False
    return True