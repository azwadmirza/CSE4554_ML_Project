def add_field(doc, name, value):
    if isinstance(value, (list, set)):
        for v in value:
            add_field(doc, name, v)
        return
    else:
        field = Element("field", name=name)
        if not isinstance(value, six.string_types):
            value = str(value)
        try:
            value = strip_bad_char(value)
            if isinstance(value, str):
                value = value.decode('utf-8')
            field.text = normalize('NFC', value)
        except:
            logger.error('Error in normalizing %r', value)
            raise
        doc.append(field)