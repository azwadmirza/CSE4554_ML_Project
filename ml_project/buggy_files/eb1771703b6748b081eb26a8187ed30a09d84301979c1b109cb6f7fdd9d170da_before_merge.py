    def _recv_internal(self, timeout):
        if timeout is not None:
            self.serialPortOrig.timeout = timeout

        canId = None
        remote = False
        extended = False
        frame = []
        readStr = self.serialPort.readline()
        if not readStr:
            return None, False
        else:
            if readStr[0] == 'T':
                # extended frame
                canId = int(readStr[1:9], 16)
                dlc = int(readStr[9])
                extended = True
                for i in range(0, dlc):
                    frame.append(int(readStr[10 + i * 2:12 + i * 2], 16))
            elif readStr[0] == 't':
                # normal frame
                canId = int(readStr[1:4], 16)
                dlc = int(readStr[4])
                for i in range(0, dlc):
                    frame.append(int(readStr[5 + i * 2:7 + i * 2], 16))
            elif readStr[0] == 'r':
                # remote frame
                canId = int(readStr[1:4], 16)
                remote = True
            elif readStr[0] == 'R':
                # remote extended frame
                canId = int(readStr[1:9], 16)
                extended = True
                remote = True

            if canId is not None:
                msg = Message(arbitration_id=canId,
                              extended_id=extended,
                              timestamp=time.time(),   # Better than nothing...
                              is_remote_frame=remote,
                              dlc=dlc,
                              data=frame)
                return msg, False
            else:
                return None, False