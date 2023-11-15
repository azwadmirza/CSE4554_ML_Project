    def __new__(meta_cls, class_name, bases, class_dict):
        '''

        '''
        names_with_refs = set()
        container_names = set()

        # Now handle all the Override
        overridden_defaults = {}
        for name, prop in class_dict.items():
            if not isinstance(prop, Override):
                continue
            if prop.default_overridden:
                overridden_defaults[name] = prop.default

        for name, default in overridden_defaults.items():
            del class_dict[name]

        generators = dict()
        for name, generator in class_dict.items():
            if isinstance(generator, PropertyDescriptorFactory):
                generators[name] = generator
            elif isinstance(generator, type) and issubclass(generator, PropertyDescriptorFactory):
                # Support the user adding a property without using parens,
                # i.e. using just the Property subclass instead of an
                # instance of the subclass
                generators[name] = generator.autocreate()

        dataspecs = {}
        new_class_attrs = {}

        for name, generator in generators.items():
            prop_descriptors = generator.make_descriptors(name)
            replaced_self = False
            for prop_descriptor in prop_descriptors:
                if prop_descriptor.name in generators:
                    if generators[prop_descriptor.name] is generator:
                        # a generator can replace itself, this is the
                        # standard case like `foo = Int()`
                        replaced_self = True
                        prop_descriptor.add_prop_descriptor_to_class(class_name, new_class_attrs, names_with_refs, container_names, dataspecs)
                    else:
                        # if a generator tries to overwrite another
                        # generator that's been explicitly provided,
                        # use the prop that was manually provided
                        # and ignore this one.
                        pass
                else:
                    prop_descriptor.add_prop_descriptor_to_class(class_name, new_class_attrs, names_with_refs, container_names, dataspecs)
            # if we won't overwrite ourselves anyway, delete the generator
            if not replaced_self:
                del class_dict[name]

        class_dict.update(new_class_attrs)

        class_dict["__properties__"] = set(new_class_attrs)
        class_dict["__properties_with_refs__"] = names_with_refs
        class_dict["__container_props__"] = container_names
        if len(overridden_defaults) > 0:
            class_dict["__overridden_defaults__"] = overridden_defaults
        if dataspecs:
            class_dict["__dataspecs__"] = dataspecs

        if "__example__" in class_dict:
            path = class_dict["__example__"]
            class_dict["__doc__"] += _EXAMPLE_TEMPLATE % dict(path=path)

        return super(MetaHasProps, meta_cls).__new__(meta_cls, class_name, bases, class_dict)