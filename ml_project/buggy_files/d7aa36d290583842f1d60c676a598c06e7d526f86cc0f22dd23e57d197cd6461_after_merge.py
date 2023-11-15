def __need_to_keep__(name):
    return name in [
        'StaticInput', 'SubsequenceInput', 'GeneratedInput', 'LayerType',
        'layer_support'
    ]