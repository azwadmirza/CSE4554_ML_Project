    def buildPacket(self, message):
        """
        Creates a ready to send modbus packet

        :param message: The populated request/response to send
        """
        data = message.encode()
        packet = struct.pack(RTU_FRAME_HEADER,
                             message.unit_id,
                             message.function_code) + data
        packet += struct.pack(">H", computeCRC(packet))
        message.transaction_id = message.unit_id  # Ensure that transaction is actually the unit id for serial comms
        return packet