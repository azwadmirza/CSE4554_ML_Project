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
      AttributeContainer|dict|list|tuple: deserialized object.

    Raises:
      ValueError: if the class type, container type or attribute type
          of event data container is not supported.
    """
    # Use __type__ to indicate the object class type.
    class_type = json_dict.get('__type__', None)
    if not class_type:
      # Dealing with a regular dict.
      return json_dict

    if class_type == 'bytes':
      return binascii.a2b_qp(json_dict['stream'])

    if class_type == 'tuple':
      return tuple(cls._ConvertListToObject(json_dict['values']))

    if class_type == 'collections.Counter':
      return cls._ConvertDictToCollectionsCounter(json_dict)

    if class_type == 'AttributeContainer':
      # Use __container_type__ to indicate the attribute container type.
      container_type = json_dict.get('__container_type__', None)

    # Since we would like the JSON as flat as possible we handle decoding
    # a path specification.
    elif class_type == 'PathSpec':
      return cls._ConvertDictToPathSpec(json_dict)

    else:
      raise ValueError('Unsupported class type: {0:s}'.format(class_type))

    container_object = (
        containers_manager.AttributeContainersManager.CreateAttributeContainer(
            container_type))

    supported_attribute_names = container_object.GetAttributeNames()
    for attribute_name, attribute_value in iter(json_dict.items()):
      # Be strict about which attributes to set in non event data attribute
      # containers.
      if (container_type != 'event_data' and
          attribute_name not in supported_attribute_names):

        if attribute_name not in ('__container_type__', '__type__'):
          logger.debug((
              '[ConvertDictToObject] unsupported attribute name: '
              '{0:s}.{1:s}').format(container_type, attribute_name))

        continue

      if isinstance(attribute_value, dict):
        attribute_value = cls._ConvertDictToObject(attribute_value)

      elif isinstance(attribute_value, list):
        attribute_value = cls._ConvertListToObject(attribute_value)

      if container_type == 'event_data':
        if isinstance(attribute_value, py2to3.BYTES_TYPE):
          raise ValueError((
              'Event data attribute value: {0:s} of type bytes is not '
              'supported.').format(attribute_name))

        if isinstance(attribute_value, dict):
          raise ValueError((
              'Event data attribute value: {0:s} of type dict is not '
              'supported.').format(attribute_name))

      setattr(container_object, attribute_name, attribute_value)

    return container_object