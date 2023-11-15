    def post_validate(self, templar):
        '''
        we can't tell that everything is of the right type until we have
        all the variables.  Run basic types (from isa) as well as
        any _post_validate_<foo> functions.
        '''

        # save the omit value for later checking
        omit_value = templar._available_variables.get('omit')

        for (name, attribute) in iteritems(self._valid_attrs):

            if getattr(self, name) is None:
                if not attribute.required:
                    continue
                else:
                    raise AnsibleParserError("the field '%s' is required but was not set" % name)
            elif not attribute.always_post_validate and self.__class__.__name__ not in ('Task', 'Handler', 'PlayContext'):
                # Intermediate objects like Play() won't have their fields validated by
                # default, as their values are often inherited by other objects and validated
                # later, so we don't want them to fail out early
                continue

            try:
                # Run the post-validator if present. These methods are responsible for
                # using the given templar to template the values, if required.
                method = getattr(self, '_post_validate_%s' % name, None)
                if method:
                    value = method(attribute, getattr(self, name), templar)
                elif attribute.isa == 'class':
                    value = getattr(self, name)
                else:
                    # if the attribute contains a variable, template it now
                    value = templar.template(getattr(self, name))

                # if this evaluated to the omit value, set the value back to
                # the default specified in the FieldAttribute and move on
                if omit_value is not None and value == omit_value:
                    setattr(self, name, attribute.default)
                    continue

                # and make sure the attribute is of the type it should be
                if value is not None:
                    if attribute.isa == 'string':
                        value = to_text(value)
                    elif attribute.isa == 'int':
                        value = int(value)
                    elif attribute.isa == 'float':
                        value = float(value)
                    elif attribute.isa == 'bool':
                        value = boolean(value, strict=False)
                    elif attribute.isa == 'percent':
                        # special value, which may be an integer or float
                        # with an optional '%' at the end
                        if isinstance(value, string_types) and '%' in value:
                            value = value.replace('%', '')
                        value = float(value)
                    elif attribute.isa == 'list':
                        if value is None:
                            value = []
                        elif not isinstance(value, list):
                            value = [value]
                        if attribute.listof is not None:
                            for item in value:
                                if not isinstance(item, attribute.listof):
                                    raise AnsibleParserError("the field '%s' should be a list of %s, "
                                                             "but the item '%s' is a %s" % (name, attribute.listof, item, type(item)), obj=self.get_ds())
                                elif attribute.required and attribute.listof == string_types:
                                    if item is None or item.strip() == "":
                                        raise AnsibleParserError("the field '%s' is required, and cannot have empty values" % (name,), obj=self.get_ds())
                    elif attribute.isa == 'set':
                        if value is None:
                            value = set()
                        elif not isinstance(value, (list, set)):
                            if isinstance(value, string_types):
                                value = value.split(',')
                            else:
                                # Making a list like this handles strings of
                                # text and bytes properly
                                value = [value]
                        if not isinstance(value, set):
                            value = set(value)
                    elif attribute.isa == 'dict':
                        if value is None:
                            value = dict()
                        elif not isinstance(value, dict):
                            raise TypeError("%s is not a dictionary" % value)
                    elif attribute.isa == 'class':
                        if not isinstance(value, attribute.class_type):
                            raise TypeError("%s is not a valid %s (got a %s instead)" % (name, attribute.class_type, type(value)))
                        value.post_validate(templar=templar)

                # and assign the massaged value back to the attribute field
                setattr(self, name, value)
            except (TypeError, ValueError) as e:
                value = getattr(self, name)
                raise AnsibleParserError("the field '%s' has an invalid value (%s), and could not be converted to an %s."
                                         "The error was: %s" % (name, value, attribute.isa, e), obj=self.get_ds(), orig_exc=e)
            except (AnsibleUndefinedVariable, UndefinedError) as e:
                if templar._fail_on_undefined_errors and name != 'name':
                    if name == 'args':
                        msg = "The task includes an option with an undefined variable. The error was: %s" % (to_native(e))
                    else:
                        msg = "The field '%s' has an invalid value, which includes an undefined variable. The error was: %s" % (name, to_native(e))
                    raise AnsibleParserError(msg, obj=self.get_ds(), orig_exc=e)

        self._finalized = True