def validate_sku_update(sku_parameter):
    """Validates a registry SKU update parameter.
    :param object sku_parameter: The registry SKU update parameter
    """
    if sku_parameter is None:
        return

    if isinstance(sku_parameter, dict):
        if 'name' not in sku_parameter or sku_parameter['name'] not in MANAGED_REGISTRY_SKU:
            _invalid_sku_update()
    elif isinstance(sku_parameter, Sku):
        if sku_parameter.name not in MANAGED_REGISTRY_SKU:
            _invalid_sku_update()
    else:
        _invalid_sku_update()