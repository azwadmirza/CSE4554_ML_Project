def _recursively_mask_objects(object_to_mask, blacklisted_object, mask_with, globbing_enabled):
    '''
    This function is used by ``_mask_object()`` to mask passwords contained in
    an osquery data structure (formed as a list of dicts, usually). Since the
    lists can sometimes be nested, recurse through the lists.

    object_to_mask
        data structure to mask recursively

    blacklisted_object
        the blacklisted_objects entry from the mask.yaml

    mask_with
        masked values are replaced with this string
    
    globbing_enabled
        enable globbing in specified blacklisted patterns of mask file
    '''
    if isinstance(object_to_mask, list):
        for child in object_to_mask:
            log.debug("Recursing object {0}".format(child))
            _recursively_mask_objects(child, blacklisted_object, mask_with, globbing_enabled)
    elif globbing_enabled and blacklisted_object['attribute_to_check'] in object_to_mask:
        mask = False
        for blacklisted_pattern in blacklisted_object['blacklisted_patterns']:
            if fnmatch.fnmatch(object_to_mask[blacklisted_object['attribute_to_check']], blacklisted_pattern):
                mask = True
                log.info("Attribute {0} will be masked.".format(object_to_mask[blacklisted_object['attribute_to_check']]))
                break
        if mask:
            for key in blacklisted_object['attributes_to_mask']:
                if key in object_to_mask:
                    object_to_mask[key] = mask_with
    elif (not globbing_enabled) and blacklisted_object['attribute_to_check'] in object_to_mask and \
         object_to_mask[blacklisted_object['attribute_to_check']] in blacklisted_object['blacklisted_patterns']:
        for key in blacklisted_object['attributes_to_mask']:
            if key in object_to_mask:
                object_to_mask[key] = mask_with