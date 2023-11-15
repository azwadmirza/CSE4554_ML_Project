    def __iter__(self):
        tail = b""
        while True:
            data = self.fp.read(OBJ_HEADER_BASE_STRUCT.size)
            if not data:
                # EOF
                break

            header = OBJ_HEADER_BASE_STRUCT.unpack(data)
            #print(header)
            if header[0] != b"LOBJ":
                raise BLFParseError()
            obj_type = header[4]
            obj_data_size = header[3] - OBJ_HEADER_BASE_STRUCT.size
            obj_data = self.fp.read(obj_data_size)
            # Read padding bytes
            self.fp.read(obj_data_size % 4)

            if obj_type == LOG_CONTAINER:
                method, uncompressed_size = LOG_CONTAINER_STRUCT.unpack_from(
                    obj_data)
                container_data = obj_data[LOG_CONTAINER_STRUCT.size:]
                if method == NO_COMPRESSION:
                    data = container_data
                elif method == ZLIB_DEFLATE:
                    data = zlib.decompress(container_data, 15, uncompressed_size)
                else:
                    # Unknown compression method
                    LOG.warning("Unknown compression method (%d)", method)
                    continue

                if tail:
                    data = tail + data
                pos = 0
                while pos + OBJ_HEADER_BASE_STRUCT.size < len(data):
                    header = OBJ_HEADER_BASE_STRUCT.unpack_from(data, pos)
                    #print(header)
                    if header[0] != b"LOBJ":
                        raise BLFParseError()

                    obj_size = header[3]
                    # Calculate position of next object
                    next_pos = pos + obj_size + (obj_size % 4)
                    if next_pos > len(data):
                        # Object continues in next log container
                        break
                    pos += OBJ_HEADER_BASE_STRUCT.size

                    # Read rest of header
                    header_version = header[2]
                    if header_version == 1:
                        flags, _, _, timestamp = OBJ_HEADER_V1_STRUCT.unpack_from(data, pos)
                        pos += OBJ_HEADER_V1_STRUCT.size
                    elif header_version == 2:
                        flags, _, _, timestamp, _ = OBJ_HEADER_V2_STRUCT.unpack_from(data, pos)
                        pos += OBJ_HEADER_V2_STRUCT.size
                    else:
                        # Unknown header version
                        LOG.warning("Unknown object header version (%d)", header_version)
                        pos = next_pos
                        continue

                    if flags == TIME_TEN_MICS:
                        factor = 10 * 1e-6
                    else:
                        factor = 1e-9
                    timestamp = timestamp * factor + self.start_timestamp

                    obj_type = header[4]
                    # Both CAN message types have the same starting content
                    if obj_type in (CAN_MESSAGE, CAN_MESSAGE2):
                        (channel, flags, dlc, can_id,
                         can_data) = CAN_MSG_STRUCT.unpack_from(data, pos)
                        msg = Message(timestamp=timestamp,
                                      arbitration_id=can_id & 0x1FFFFFFF,
                                      extended_id=bool(can_id & CAN_MSG_EXT),
                                      is_remote_frame=bool(flags & REMOTE_FLAG),
                                      dlc=dlc,
                                      data=can_data[:dlc],
                                      channel=channel - 1)
                        yield msg
                    elif obj_type == CAN_FD_MESSAGE:
                        (channel, flags, dlc, can_id, _, _, fd_flags,
                         _, can_data) = CAN_FD_MSG_STRUCT.unpack_from(data, pos)
                        length = dlc2len(dlc)
                        msg = Message(timestamp=timestamp,
                                      arbitration_id=can_id & 0x1FFFFFFF,
                                      extended_id=bool(can_id & CAN_MSG_EXT),
                                      is_remote_frame=bool(flags & REMOTE_FLAG),
                                      is_fd=bool(fd_flags & EDL),
                                      bitrate_switch=bool(fd_flags & BRS),
                                      error_state_indicator=bool(fd_flags & ESI),
                                      dlc=length,
                                      data=can_data[:length],
                                      channel=channel - 1)
                        yield msg
                    elif obj_type == CAN_ERROR_EXT:
                        (channel, _, _, _, _, dlc, _, can_id, _,
                         can_data) = CAN_ERROR_EXT_STRUCT.unpack_from(data, pos)
                        msg = Message(timestamp=timestamp,
                                      is_error_frame=True,
                                      extended_id=bool(can_id & CAN_MSG_EXT),
                                      arbitration_id=can_id & 0x1FFFFFFF,
                                      dlc=dlc,
                                      data=can_data[:dlc],
                                      channel=channel - 1)
                        yield msg

                    pos = next_pos

                # Save remaing data that could not be processed
                tail = data[pos:]

        self.fp.close()