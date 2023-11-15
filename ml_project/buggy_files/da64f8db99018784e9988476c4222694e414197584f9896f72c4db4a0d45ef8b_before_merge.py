  def _ConvertDictToObject(cls, json_dict):
    """Converts a JSON dict into an object.

    The dictionary of the JSON serialized objects consists of:
    {
        '__type__': 'AttributeContainer'
        '__container_type__': ...
        ...
    }

    Here '__type__' indicates the object base type. In this case
    'AttributeContainer'.

    '__container_type__' indicates the attribute container type.

    The rest of the elements of the dictionary make up the attributes.

    Args:
      json_dict (dict[str, object]): JSON serialized objects.

    Returns:
      A deserialized object which can be:
        * an attribute container (instance of AttributeContainer);
        * a dictionary;
        * a list;
        * a tuple.

    Raises:
      ValueError: if the class type or container type is not supported.
    """
    # Use __type__ to indicate the object class type.
    class_type = json_dict.get(u'__type__', None)
    if not class_type:
      # Dealing with a regular dict.
      return json_dict

    if class_type == u'bytes':
      return binascii.a2b_qp(json_dict[u'stream'])

    elif class_type == u'tuple':
      return tuple(cls._ConvertListToObject(json_dict[u'values']))

    elif class_type == u'collections.Counter':
      return cls._ConvertDictToCollectionsCounter(json_dict)

    elif class_type == u'AttributeContainer':
      # Use __container_type__ to indicate the attribute container type.
      container_type = json_dict.get(u'__container_type__', None)

    # Since we would like the JSON as flat as possible we handle decoding
    # a path specification.
    elif class_type == u'PathSpec':
      return cls._ConvertDictToPathSpec(json_dict)

    else:
      raise ValueError(u'Unsupported class type: {0:s}'.format(class_type))

    container_class = (
        containers_manager.AttributeContainersManager.GetAttributeContainer(
            container_type))
    if not container_class:
      raise ValueError(u'Unsupported container type: {0:s}'.format(
          container_type))

    container_object = container_class()
    for attribute_name, attribute_value in iter(json_dict.items()):
      if attribute_name.startswith(u'__'):
        continue

      # Be strict about which attributes to set in non event objects.
      if (container_type != u'event' and
          attribute_name not in container_object.__dict__):
        continue

      # Note that "_tags" is the name for "labels" in EventTag prior to
      # version 1.4.1-20160131
      if container_type == u'event_tag' and attribute_name == u'_event_tags':
        attribute_name = u'labels'

      if isinstance(attribute_value, dict):
        attribute_value = cls._ConvertDictToObject(attribute_value)

      elif isinstance(attribute_value, list):
        attribute_value = cls._ConvertListToObject(attribute_value)

      setattr(container_object, attribute_name, attribute_value)

    return container_object