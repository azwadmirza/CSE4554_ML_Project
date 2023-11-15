def _invalid_sku_update():
    raise CLIError("Please specify SKU by '--sku SKU' or '--set sku.name=SKU'. Allowed SKUs: {0}".format(
        MANAGED_REGISTRY_SKU))