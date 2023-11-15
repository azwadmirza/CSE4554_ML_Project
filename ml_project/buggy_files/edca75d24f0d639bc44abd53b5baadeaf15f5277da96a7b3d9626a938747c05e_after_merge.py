def parse_type(item, location, sigs=None, custom_units=None, custom_structs=None, constants=None):
    # Base and custom types, e.g. num
    if isinstance(item, ast.Name):
        if item.id in base_types:
            return BaseType(item.id)
        elif item.id in special_types:
            return special_types[item.id]
        elif (custom_structs is not None) and (item.id in custom_structs):
            return make_struct_type(item.id, location, custom_structs[item.id], custom_units, custom_structs, constants)
        else:
            raise InvalidTypeException("Invalid base type: " + item.id, item)
    # Units, e.g. num (1/sec) or contracts
    elif isinstance(item, ast.Call):
        # Mapping type.
        if item.func.id == 'map':
            if location == 'memory':
                raise InvalidTypeException("No mappings allowed for in-memory types, only fixed-size arrays", item)
            if len(item.args) != 2:
                raise InvalidTypeException("Mapping requires 2 valid positional arguments.", item)
            keytype = parse_type(item.args[0], None, custom_units=custom_units, custom_structs=custom_structs, constants=constants)
            if not isinstance(keytype, (BaseType, ByteArrayType)):
                raise InvalidTypeException("Mapping keys must be base or bytes types", item)
            return MappingType(keytype, parse_type(item.args[1], location, custom_units=custom_units, custom_structs=custom_structs, constants=constants))
        # Contract_types
        if item.func.id == 'address':
            if sigs and item.args[0].id in sigs:
                return ContractType(item.args[0].id)
        # Struct types
        if (custom_structs is not None) and (item.func.id in custom_structs):
            return make_struct_type(item.id, location, custom_structs[item.id], custom_units, custom_structs)
        if not isinstance(item.func, ast.Name):
            raise InvalidTypeException("Malformed unit type:", item)
        base_type = item.func.id
        if base_type not in ('int128', 'uint256', 'decimal'):
            raise InvalidTypeException("You must use int128, uint256, decimal, address, contract, \
                for variable declarations and indexed for logging topics ", item)
        if len(item.args) == 0:
            raise InvalidTypeException("Malformed unit type", item)
        if isinstance(item.args[-1], ast.Name) and item.args[-1].id == "positional":
            positional = True
            argz = item.args[:-1]
        else:
            positional = False
            argz = item.args
        if len(argz) != 1:
            raise InvalidTypeException("Malformed unit type", item)
        unit = parse_unit(argz[0], custom_units=custom_units)
        return BaseType(base_type, unit, positional)
    # Subscripts
    elif isinstance(item, ast.Subscript):

        if 'value' not in vars(item.slice):
            raise InvalidTypeException("Array / ByteArray access must access a single element, not a slice", item)
        # Fixed size lists or bytearrays, e.g. num[100]
        is_constant_val = constants.ast_is_constant(item.slice.value)
        if isinstance(item.slice.value, ast.Num) or is_constant_val:
            n_val = constants.get_constant(item.slice.value.id, context=None).value if is_constant_val else item.slice.value.n
            if not isinstance(n_val, int) or n_val <= 0:
                raise InvalidTypeException("Arrays / ByteArrays must have a positive integral number of elements", item.slice.value)
            # ByteArray
            if getattr(item.value, 'id', None) == 'bytes':
                return ByteArrayType(n_val)
            # List
            else:
                return ListType(parse_type(item.value, location, custom_units=custom_units, custom_structs=custom_structs, constants=constants), n_val)
        # Mappings, e.g. num[address]
        else:
            warnings.warn(
                "Mapping definitions using subscript have deprecated (see VIP564). "
                "Use map(type1, type2) instead.",
                DeprecationWarning
            )
            raise InvalidTypeException('Unknown list type.', item)

    # Dicts, used to represent mappings, e.g. {uint: uint}. Key must be a base type
    elif isinstance(item, ast.Dict):
        warnings.warn(
            "Anonymous structs have been removed in"
            " favor of named structs, see VIP300",
            DeprecationWarning
        )
        raise InvalidTypeException("Invalid type: %r" % ast.dump(item), item)
    elif isinstance(item, ast.Tuple):
        members = [parse_type(x, location, custom_units=custom_units, custom_structs=custom_structs, constants=constants) for x in item.elts]
        return TupleType(members)
    else:
        raise InvalidTypeException("Invalid type: %r" % ast.dump(item), item)