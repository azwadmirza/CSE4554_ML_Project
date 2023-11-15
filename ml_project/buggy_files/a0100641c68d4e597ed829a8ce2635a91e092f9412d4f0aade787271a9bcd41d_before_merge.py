def get_signals(signal_array, frame, ea, multiplex_id, float_factory, bit_offset=0):
    # type: (typing.Sequence[_Element], canmatrix.Frame, _DocRoot, str, _MultiplexId, typing.Callable, int) -> None
    """Add signals from xml to the Frame."""
    global signal_rxs
    group_id = 1
    if signal_array is None:  # Empty signalarray - nothing to do
        return
    for signal in signal_array:
        compu_method = None
        motorola = ea.get_child(signal, "PACKING-BYTE-ORDER")
        start_bit = ea.get_child(signal, "START-POSITION")

        isignal = ea.follow_ref(signal, "SIGNAL-REF")
        if isignal is None:
            isignal = ea.follow_ref(signal, "I-SIGNAL-REF")

        if isignal is None:
            isignal = ea.follow_ref(signal, "I-SIGNAL-GROUP-REF")
            if isignal is not None:
                logger.debug("get_signals: found I-SIGNAL-GROUP ")

                isignal_array = ea.find_children_by_path(isignal, "I-SIGNAL")
                system_signal_array = [ea.follow_ref(isignal, "SYSTEM-SIGNAL-REF") for isignal in isignal_array]
                system_signal_group = ea.follow_ref(isignal, "SYSTEM-SIGNAL-GROUP-REF")
                get_sys_signals(system_signal_group, system_signal_array, frame, group_id, ea)
                group_id = group_id + 1
                continue
        if isignal is None:
            logger.debug(
                'Frame %s, no isignal for %s found',
                frame.name, ea.get_child(signal, "SHORT-NAME").text)

        base_type = ea.follow_ref(isignal, "BASE-TYPE-REF")
        try:
            type_encoding = ea.get_child(base_type, "BASE-TYPE-ENCODING").text
        except AttributeError:
            type_encoding = "None"
        signal_name = None  # type: typing.Optional[str]
        signal_name_elem = ea.get_child(isignal, "LONG-NAME")
        if signal_name_elem is not None:
            signal_name_elem = ea.get_child(signal_name_elem, "L-4")
            if signal_name_elem is not None:
                signal_name = signal_name_elem.text

        system_signal = ea.follow_ref(isignal, "SYSTEM-SIGNAL-REF")

        if system_signal is None:
            logger.debug('Frame %s, signal %s has no system-signal', frame.name, isignal.tag)

        if system_signal is not None and "SYSTEM-SIGNAL-GROUP" in system_signal.tag:
            system_signals = ea.find_children_by_path(system_signal, "SYSTEM-SIGNAL-REFS/SYSTEM-SIGNAL")
            get_sys_signals(system_signal, system_signals, frame, group_id, ns)
            group_id = group_id + 1
            continue

        length = ea.get_child(isignal, "LENGTH")
        if length is None:
            length = ea.get_child(system_signal, "LENGTH")

        name = ea.get_child(system_signal, "SHORT-NAME")
        unit_element = ea.get_child(isignal, "UNIT")
        display_name = ea.get_child(unit_element, "DISPLAY-NAME")
        if display_name is not None:
            signal_unit = display_name.text
        else:
            signal_unit = ""

        signal_min = None  # type: canmatrix.types.OptionalPhysicalValue
        signal_max = None  # type: canmatrix.types.OptionalPhysicalValue
        receiver = []  # type: typing.List[str]

        signal_description = ea.get_element_desc(system_signal)

        datatype = ea.follow_ref(system_signal, "DATA-TYPE-REF")
        if datatype is None:  # AR4?
            data_constr = None
            compu_method = None
            base_type = None
            for test_signal in [isignal, system_signal]:
                if data_constr is None:
                    data_constr = ea.follow_ref(test_signal, "DATA-CONSTR-REF")
                if compu_method is None:
                    compu_method = ea.follow_ref(test_signal, "COMPU-METHOD-REF")
                if base_type is None:
                    base_type = ea.follow_ref(test_signal, "BASE-TYPE-REF")

            lower = ea.get_child(data_constr, "LOWER-LIMIT")
            upper = ea.get_child(data_constr, "UPPER-LIMIT")
            encoding = None  # TODO - find encoding in AR4
        else:
            lower = ea.get_child(datatype, "LOWER-LIMIT")
            upper = ea.get_child(datatype, "UPPER-LIMIT")
            type_encoding = ea.get_child(datatype, "ENCODING")

        if lower is not None and upper is not None:
            signal_min = float_factory(lower.text)
            signal_max = float_factory(upper.text)

        datdefprops = ea.get_child(datatype, "SW-DATA-DEF-PROPS")

        if compu_method is None:
            compu_method = ea.follow_ref(datdefprops, "COMPU-METHOD-REF")
        if compu_method is None:  # AR4
            compu_method = ea.get_child(isignal, "COMPU-METHOD")
            base_type = ea.follow_ref(isignal, "BASE-TYPE-REF")
            encoding = ea.get_child(base_type, "BASE-TYPE-ENCODING")
            if encoding is not None and encoding.text == "IEEE754":
                is_float = True
        if compu_method is None:
            logger.debug('No Compmethod found!! - try alternate scheme 1.')
            networkrep = ea.get_child(isignal, "NETWORK-REPRESENTATION-PROPS")
            data_def_props_var = ea.get_child(networkrep, "SW-DATA-DEF-PROPS-VARIANTS")
            data_def_props_cond = ea.get_child(data_def_props_var, "SW-DATA-DEF-PROPS-CONDITIONAL")
            if data_def_props_cond is not None:
                try:
                    compu_method = ea.get_child(data_def_props_cond, "COMPU-METHOD")
                except:
                    logger.debug('No valid compu method found for this - check ARXML file!!')
                    compu_method = None
        #####################################################################################################
        # no found compu-method fuzzy search in systemsignal:
        #####################################################################################################
        if compu_method is None:
            logger.debug('No Compmethod found!! - fuzzy search in syssignal.')
            compu_method = ea.get_child(system_signal, "COMPU-METHOD")

        # decode compuMethod:
        (values, factor, offset, unit_elem, const) = decode_compu_method(compu_method, ea, float_factory)

        if signal_min is not None:
            signal_min *= factor
            signal_min += offset
        if signal_max is not None:
            signal_max *= factor
            signal_max += offset

        if base_type is None:
            base_type = ea.get_child(datdefprops, "BASE-TYPE")

        (is_signed, is_float) = eval_type_of_signal(type_encoding, base_type, ea)

        if unit_elem is not None:
            longname = ea.get_child(unit_elem, "LONG-NAME")
        #####################################################################################################
        # Modification to support obtaining the Signals Unit by DISPLAY-NAME. 07June16
        #####################################################################################################
            display_name = None
            try:
                display_name = ea.get_child(unit_elem, "DISPLAY-NAME")
            except:
                logger.debug('No Unit Display name found!! - using long name')
            if display_name is not None:
                signal_unit = display_name.text
            else:
                l4 = ea.get_child(longname, "L-4")
                if l4 is not None:
                    signal_unit = l4.text

        init_list = ea.find_children_by_path(system_signal, "INIT-VALUE/VALUE")

        if not init_list:
            init_list = ea.find_children_by_path(isignal, "INIT-VALUE/NUMERICAL-VALUE-SPECIFICATION/VALUE")  # #AR4.2
        if init_list:
            initvalue = init_list[0]
        else:
            initvalue = None

        is_little_endian = False
        if motorola is not None:
            if motorola.text == 'MOST-SIGNIFICANT-BYTE-LAST':
                is_little_endian = True
        else:
            logger.debug('no name byte order for signal' + name.text)

        if name is None:
            logger.debug('no name for signal given')
            name = ea.get_child(isignal, "SHORT-NAME")
        if start_bit is None:
            logger.debug('no startBit for signal given')
        if length is None:
            logger.debug('no length for signal given')

        if start_bit is not None:
            new_signal = canmatrix.Signal(
                name.text,
                start_bit=int(start_bit.text) + bit_offset,
                size=int(length.text) if length is not None else 0,
                is_little_endian=is_little_endian,
                is_signed=is_signed,
                factor=factor,
                offset=offset,
                unit=signal_unit,
                receivers=receiver,
                multiplex=multiplex_id,
                comment=signal_description,
                is_float=is_float)

            if signal_min is not None:
                new_signal.min = signal_min
            if signal_max is not None:
                new_signal.max = signal_max

            if not new_signal.is_little_endian:
                # startbit of motorola coded signals are MSB in arxml
                new_signal.set_startbit(int(start_bit.text) + bit_offset, bitNumbering=1)

            # save signal, to determin receiver-ECUs for this signal later
            signal_rxs[system_signal] = new_signal

            if base_type is not None:
                temp = ea.get_child(base_type, "SHORT-NAME")
                if temp is not None and "boolean" == temp.text:
                    new_signal.add_values(1, "TRUE")
                    new_signal.add_values(0, "FALSE")

            if initvalue is not None and initvalue.text is not None:
                initvalue.text = canmatrix.utils.guess_value(initvalue.text)
                new_signal.initial_value = float_factory(initvalue.text)

            for key, value in list(values.items()):
                new_signal.add_values(canmatrix.utils.decode_number(key), value)
            if signal_name is not None:
                new_signal.add_attribute("LongName", signal_name)
            frame.add_signal(new_signal)