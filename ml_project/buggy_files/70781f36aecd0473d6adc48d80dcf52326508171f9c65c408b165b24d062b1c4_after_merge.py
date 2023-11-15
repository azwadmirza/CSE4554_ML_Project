def validate_sku_update(current_sku, sku_parameter):
    """Validates a registry SKU update parameter.
    :param object sku_parameter: The registry SKU update parameter
    """
    if sku_parameter is None:
        return

    if isinstance(sku_parameter, dict):
        if 'name' not in sku_parameter:
            _invalid_sku_update()
        if sku_parameter['name'] not in CLASSIC_REGISTRY_SKU and sku_parameter['name'] not in MANAGED_REGISTRY_SKU:
            _invalid_sku_update()
        if current_sku in MANAGED_REGISTRY_SKU and sku_parameter['name'] in CLASSIC_REGISTRY_SKU:
            _invalid_sku_downgrade()
    elif isinstance(sku_parameter, Sku):
        if current_sku in MANAGED_REGISTRY_SKU and sku_parameter.name in CLASSIC_REGISTRY_SKU:
            _invalid_sku_downgrade()
    else:
        _invalid_sku_update()