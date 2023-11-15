def get_mors_with_properties(service_instance, object_type, property_list=None, container_ref=None):
    '''
    Returns a list containing properties and managed object references for the managed object.

    service_instance
        The Service Instance from which to obtain managed object references.

    object_type
        The type of content for which to obtain managed object references.

    property_list
        An optional list of object properties used to return even more filtered managed object reference results.

    container_ref
        An optional reference to the managed object to search under. Can either be an object of type Folder, Datacenter,
        ComputeResource, Resource Pool or HostSystem. If not specified, default behaviour is to search under the inventory
        rootFolder.
    '''
    # Get all the content
    content_args = [service_instance, object_type]
    content_kwargs = {'property_list': property_list,
                      'container_ref': container_ref,
                      }
    try:
        content = get_content(*content_args, **content_kwargs)
    except BadStatusLine:
        content = get_content(*content_args, **content_kwargs)
    except IOError as e:
        if e.errno != errno.EPIPE:
            raise e
        content = get_content(*content_args, **content_kwargs)

    object_list = []
    for obj in content:
        properties = {}
        for prop in obj.propSet:
            properties[prop.name] = prop.val
            properties['object'] = obj.obj
        object_list.append(properties)

    return object_list