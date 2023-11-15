    def add_globals_and_events(self, item):
        item_attributes = {"public": False}

        # Make sure we have a valid variable name.
        if not isinstance(item.target, ast.Name):
            raise StructureException('Invalid global variable name', item.target)

        # Handle constants.
        if self.get_call_func_name(item) == "constant":
            self._constants.add_constant(item, global_ctx=self)
            return

        # Handle events.
        if not (self.get_call_func_name(item) == "event"):
            item_name, item_attributes = self.get_item_name_and_attributes(item, item_attributes)
            if not all([attr in valid_global_keywords for attr in item_attributes.keys()]):
                raise StructureException('Invalid global keyword used: %s' % item_attributes, item)

        if item.value is not None:
            raise StructureException('May not assign value whilst defining type', item)
        elif self.get_call_func_name(item) == "event":
            if self._globals or len(self._defs):
                raise EventDeclarationException("Events must all come before global declarations and function definitions", item)
            self._events.append(item)
        elif not isinstance(item.target, ast.Name):
            raise StructureException("Can only assign type to variable in top-level statement", item)

        # Is this a custom unit definition.
        elif item.target.id == 'units':
            if not self._custom_units:
                if not isinstance(item.annotation, ast.Dict):
                    raise VariableDeclarationException("Define custom units using units: { }.", item.target)
                for key, value in zip(item.annotation.keys, item.annotation.values):
                    if not isinstance(value, ast.Str):
                        raise VariableDeclarationException("Custom unit description must be a valid string", value)
                    if not isinstance(key, ast.Name):
                        raise VariableDeclarationException("Custom unit name must be a valid string", key)
                    check_valid_varname(key.id, self._custom_units, self._structs, self._constants, key, "Custom unit invalid.")
                    self._custom_units.add(key.id)
                    self._custom_units_descriptions[key.id] = value.s
            else:
                raise VariableDeclarationException("Custom units can only be defined once", item.target)

        # Check if variable name is valid.
        # Don't move this check higher, as unit parsing has to happen first.
        elif not self.is_valid_varname(item.target.id, item):
            pass

        elif len(self._defs):
            raise StructureException("Global variables must all come before function definitions", item)
        # If the type declaration is of the form public(<type here>), then proceed with
        # the underlying type but also add getters
        elif self.get_call_func_name(item) == "address":
            if item.annotation.args[0].id not in premade_contracts:
                raise VariableDeclarationException("Unsupported premade contract declaration", item.annotation.args[0])
            premade_contract = premade_contracts[item.annotation.args[0].id]
            self._contracts[item.target.id] = self.make_contract(premade_contract.body)
            self._globals[item.target.id] = VariableRecord(item.target.id, len(self._globals), BaseType('address'), True)

        elif item_name in self._contracts:
            self._globals[item.target.id] = ContractRecord(item.target.id, len(self._globals), ContractType(item_name), True)
            if item_attributes["public"]:
                typ = ContractType(item_name)
                for getter in self.mk_getter(item.target.id, typ):
                    self._getters.append(self.parse_line('\n' * (item.lineno - 1) + getter))
                    self._getters[-1].pos = getpos(item)

        elif self.get_call_func_name(item) == "public":
            if isinstance(item.annotation.args[0], ast.Name) and item_name in self._contracts:
                typ = ContractType(item_name)
            else:
                typ = parse_type(item.annotation.args[0], 'storage', custom_units=self._custom_units, custom_structs=self._structs, constants=self._constants)
            self._globals[item.target.id] = VariableRecord(item.target.id, len(self._globals), typ, True)
            # Adding getters here
            for getter in self.mk_getter(item.target.id, typ):
                self._getters.append(self.parse_line('\n' * (item.lineno - 1) + getter))
                self._getters[-1].pos = getpos(item)

        elif isinstance(item.annotation, (ast.Name, ast.Call, ast.Subscript)):
            self._globals[item.target.id] = VariableRecord(
                item.target.id, len(self._globals),
                parse_type(item.annotation, 'storage', custom_units=self._custom_units, custom_structs=self._structs, constants=self._constants),
                True
            )
        else:
            raise InvalidTypeException('Invalid global type specified', item)