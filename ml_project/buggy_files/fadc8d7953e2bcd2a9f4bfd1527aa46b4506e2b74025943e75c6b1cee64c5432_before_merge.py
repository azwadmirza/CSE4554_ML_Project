def feature_encoding_input(block):
    """Fetch the column_types and column_names.

    The values are fetched for FeatureEncoding from StructuredDataInput.
    """
    if not isinstance(block.inputs[0], nodes.StructuredDataInput):
        raise TypeError('FeatureEncoding block can only be used '
                        'with StructuredDataInput.')
    block.column_types = block.inputs[0].column_types
    block.column_names = block.inputs[0].column_names