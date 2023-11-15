    def __getattr__(self, attr):
      """Handle unknown attributes.

      Often the actual object returned is not the object that is expected. In
      those cases attempting to retrieve a specific named attribute would
      normally raise, e.g.:

      fd = aff4.FACTORY.Open(urn)
      fd.Get(fd.Schema.DOESNTEXIST, default_value)

      In this case we return None to ensure that the default is chosen.

      However, if the caller specifies a specific aff4_type, they expect the
      attributes of that object. If they are referencing a non-existent
      attribute this is an error and we should raise, e.g.:

      fd = aff4.FACTORY.Open(urn, aff4_type=module.SomeClass)
      fd.Get(fd.Schema.DOESNTEXIST, default_value)

      Args:
        attr: Some ignored attribute.
      Raises:
        BadGetAttributeError: if the object was opened with a specific type
      """
      if self.aff4_type:
        raise BadGetAttributeError(
            "Attribute %s does not exist on object opened with aff4_type %s" %
            (utils.SmartStr(attr), self.aff4_type))

      return None