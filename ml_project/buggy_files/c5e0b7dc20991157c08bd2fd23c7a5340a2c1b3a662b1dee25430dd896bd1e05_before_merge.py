def base_type_conversion(orig, frm, to, pos):
    orig = unwrap_location(orig)
    if getattr(frm, 'is_literal', False) and frm.typ in ('int128', 'uint256') and not SizeLimits.in_bounds(frm.typ, orig.value):
        raise InvalidLiteralException("Number out of range: " + str(orig.value), pos)
    if not isinstance(frm, (BaseType, NullType)) or not isinstance(to, BaseType):
        raise TypeMismatchException("Base type conversion from or to non-base type: %r %r" % (frm, to), pos)
    elif is_base_type(frm, to.typ) and are_units_compatible(frm, to):
        return LLLnode(orig.value, orig.args, typ=to, add_gas_estimate=orig.add_gas_estimate)
    elif is_base_type(frm, 'int128') and is_base_type(to, 'decimal') and are_units_compatible(frm, to):
        return LLLnode.from_list(['mul', orig, DECIMAL_DIVISOR], typ=BaseType('decimal', to.unit, to.positional))
    elif isinstance(frm, NullType):
        if to.typ not in ('int128', 'bool', 'uint256', 'address', 'bytes32', 'decimal'):
            # This is only to future proof the use of  base_type_conversion.
            raise TypeMismatchException("Cannot convert null-type object to type %r" % to, pos)  # pragma: no cover
        return LLLnode.from_list(0, typ=to)
    elif isinstance(to, ContractType) and frm.typ == 'address':
        return LLLnode(orig.value, orig.args, typ=to, add_gas_estimate=orig.add_gas_estimate)
    # Integer literal conversion.
    elif (frm.typ, to.typ, frm.is_literal) == ('int128', 'uint256', True):
        return LLLnode(orig.value, orig.args, typ=to, add_gas_estimate=orig.add_gas_estimate)
    else:
        raise TypeMismatchException("Typecasting from base type %r to %r unavailable" % (frm, to), pos)