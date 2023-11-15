def decode_can_helper(ea, float_factory, ignore_cluster_info):
    found_matrixes = {}
    if ignore_cluster_info is True:
        ccs = [lxml.etree.Element("ignoreClusterInfo")]  # type: typing.Sequence[_Element]
    else:
        ccs = ea.findall('CAN-CLUSTER')
    for cc in ccs:  # type: _Element
        db = canmatrix.CanMatrix()
        # Defines not jet imported...
        db.add_ecu_defines("NWM-Stationsadresse", 'HEX 0 63')
        db.add_ecu_defines("NWM-Knoten", 'ENUM  "nein","ja"')
        db.add_signal_defines("LongName", 'STRING')
        db.add_frame_defines("GenMsgDelayTime", 'INT 0 65535')
        db.add_frame_defines("GenMsgNrOfRepetitions", 'INT 0 65535')
        db.add_frame_defines("GenMsgStartValue", 'STRING')
        db.add_frame_defines("GenMsgStartDelayTime", 'INT 0 65535')
        db.add_frame_defines(
            "GenMsgSendType",
            'ENUM  "cyclicX","spontanX","cyclicIfActiveX","spontanWithDelay","cyclicAndSpontanX","cyclicAndSpontanWithDelay","spontanWithRepitition","cyclicIfActiveAndSpontanWD","cyclicIfActiveFast","cyclicWithRepeatOnDemand","none"')

        if ignore_cluster_info is True:
            can_frame_trig = ea.findall('CAN-FRAME-TRIGGERING')
            bus_name = ""
        else:
            speed = ea.get_child(cc, "SPEED")
            baudrate_elem = ea.find("BAUDRATE", cc)
            fd_baudrate_elem = ea.find("CAN-FD-BAUDRATE", cc)

            logger.debug("Busname: " + ea.get_element_name(cc))

            bus_name = ea.get_element_name(cc)
            if speed is not None:
                db.baudrate = int(speed.text)
            elif baudrate_elem is not None:
                db.baudrate = int(baudrate_elem.text)

            logger.debug("Baudrate: "+ str(db.baudrate))
            if fd_baudrate_elem is not None:
                db.fd_baudrate = fd_baudrate_elem.text

        

            physical_channels = ea.find("PHYSICAL-CHANNELS", cc)  # type: _Element
            if physical_channels is None:
                logger.error("PHYSICAL-CHANNELS not found")

            nm_lower_id = ea.get_child(cc, "NM-LOWER-CAN-ID")

            physical_channel = ea.get_child(physical_channels, "PHYSICAL-CHANNEL")
            if physical_channel is None:
                physical_channel = ea.get_child(physical_channels, "CAN-PHYSICAL-CHANNEL")
            if physical_channel is None:
                logger.error("PHYSICAL-CHANNEL not found")
            can_frame_trig = ea.get_children(physical_channel, "CAN-FRAME-TRIGGERING")
            if can_frame_trig is None:
                logger.error("CAN-FRAME-TRIGGERING not found")
            else:
                logger.debug("%d frames found in arxml", len(can_frame_trig))

        multiplex_translation = {}  # type: typing.Dict[str, str]
        for frameTrig in can_frame_trig:  # type: _Element
            frame = get_frame(frameTrig, ea, multiplex_translation, float_factory)
            if frame is not None:
                db.add_frame(frame)

        if ignore_cluster_info is True:
            pass
            # no support for signal direction
        else:  # find signal senders/receivers...
            isignal_triggerings = ea.find_children_by_path(physical_channel, "I-SIGNAL-TRIGGERING")
            for sig_trig in isignal_triggerings:
                isignal = ea.follow_ref(sig_trig, 'SIGNAL-REF')
                if isignal is None:
                    isignal = ea.follow_ref(sig_trig, 'I-SIGNAL-REF')
                if isignal is None:
                    sig_trig_text = ea.get_element_name(sig_trig) if sig_trig is not None else "None"
                    logger.debug("load: no isignal for %s", sig_trig_text)
                    continue

                port_ref = ea.follow_all_ref(sig_trig, "I-SIGNAL-PORT-REF")

                for port in port_ref:
                    comm_direction = ea.get_child(port, "COMMUNICATION-DIRECTION")
                    if comm_direction is not None and comm_direction.text == "IN":
                        sys_signal = ea.follow_ref(isignal, "SYSTEM-SIGNAL-REF")
                        ecu_name = ea.get_element_name(port.getparent().getparent().getparent().getparent())
                        # port points in ECU; probably more stable to go up
                        # from each ECU than to go down in XML...
                        if sys_signal in signal_rxs:
                            signal_rxs[sys_signal].add_receiver(ecu_name)
                            # find ECUs:
        nodes = ea.findall('ECU-INSTANCE')
        for node in nodes:  # type: _Element
            ecu = process_ecu(node, db, ea, multiplex_translation)
            desc = ea.get_child(node, "DESC", )
            l2 = ea.get_child(desc, "L-2")
            if l2 is not None:
                ecu.add_comment(l2.text)

            db.add_ecu(ecu)

        if 0:
        #for frame in db.frames:
            sig_value_hash = dict()
            for sig in frame.signals:
                try:
                    sig_value_hash[sig.name] = sig.phys2raw()
                except AttributeError:
                    sig_value_hash[sig.name] = 0
            frame_data = frame.encode(sig_value_hash)
            frame.add_attribute("GenMsgStartValue", "".join(["%02x" % x for x in frame_data]))
        found_matrixes[bus_name] = db
    return found_matrixes