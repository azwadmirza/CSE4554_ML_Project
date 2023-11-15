def is_horizons(economies: MAP_STR_ANY, modules: Dict, ships: MAP_STR_ANY) -> bool:
    return (
        any(economy['name'] == 'Colony' for economy in economies.values()) or
        any(module.get('sku') == HORIZ_SKU for module in modules.values()) or
        any(ship.get('sku') == HORIZ_SKU for ship in (ships['shipyard_list'] or {}).values())
    )