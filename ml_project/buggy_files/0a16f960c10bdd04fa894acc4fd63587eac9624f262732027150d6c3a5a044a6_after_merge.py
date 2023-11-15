def smartos():
    '''
    Provide grains for SmartOS
    '''
    grains = {}

    if salt.utils.platform.is_smartos_zone():
        grains = salt.utils.dictupdate.update(grains, _smartos_zone_data(), merge_lists=True)
    elif salt.utils.platform.is_smartos_globalzone():
        grains = salt.utils.dictupdate.update(grains, _smartos_computenode_data(), merge_lists=True)
    grains = salt.utils.dictupdate.update(grains, _smartos_zone_pkgin_data(), merge_lists=True)
    grains = salt.utils.dictupdate.update(grains, _smartos_zone_pkgsrc_data(), merge_lists=True)

    return grains