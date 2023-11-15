def decode_compu_method(compu_method, ea, float_factory):
    # type: (_Element, _DocRoot, str, _FloatFactory) -> typing.Tuple
    values = {}
    factor = float_factory(1.0)
    offset = float_factory(0)
    unit = ea.follow_ref(compu_method, "UNIT-REF")
    const = None
    compu_scales = ea.find_children_by_path(compu_method, "COMPU-INTERNAL-TO-PHYS/COMPU-SCALES/COMPU-SCALE")
    for compu_scale in compu_scales:
        ll = ea.get_child(compu_scale, "LOWER-LIMIT")
        ul = ea.get_child(compu_scale, "UPPER-LIMIT")
        sl = ea.get_child(compu_scale, "SHORT-LABEL")
        if sl is None:
            desc = ea.get_element_desc(compu_scale)
        else:
            desc = sl.text
        #####################################################################################################
        # Modification to support sourcing the COMPU_METHOD info from the Vector NETWORK-REPRESENTATION-PROPS
        # keyword definition. 06Jun16
        #####################################################################################################

        if ll is not None and desc is not None and canmatrix.utils.decode_number(ul.text, float_factory) == canmatrix.utils.decode_number(ll.text, float_factory):
            #####################################################################################################
            #####################################################################################################
            values[ll.text] = desc

        scale_desc = ea.get_element_desc(compu_scale)
        rational = ea.get_child(compu_scale, "COMPU-RATIONAL-COEFFS")
        if rational is not None:
            numerator_parent = ea.get_child(rational, "COMPU-NUMERATOR")
            numerator = ea.get_children(numerator_parent, "V")
            denominator_parent = ea.get_child(rational, "COMPU-DENOMINATOR")
            denominator = ea.get_children(denominator_parent, "V")
            try:
                factor = float_factory(numerator[1].text) / float_factory(denominator[0].text)
                offset = float_factory(numerator[0].text) / float_factory(denominator[0].text)
            except decimal.DivisionByZero:
                if numerator[0].text != denominator[0].text or numerator[1].text != denominator[1].text:
                    logger.warning("ARXML signal scaling: polynom is not supported and it is replaced by factor=1 and offset =0.")
                factor = float_factory(1)
                offset = float_factory(0)
        else:
            const = ea.get_child(compu_scale, "COMPU-CONST")
            # add value
            if const is None:
                logger.warning("Unknown Compu-Method: at sourceline %d ", compu_method.sourceline)
    return values, factor, offset, unit, const