    def getByteStream(self, fileinfo):

        message = slskmessages.SlskMessage()

        stream = bytearray()
        stream.extend(bytes([1]) + message.packObject(fileinfo[0]) + message.packObject(NetworkLongLongType(fileinfo[1])))
        if fileinfo[2] is not None:
            try:
                msgbytes = bytearray()
                msgbytes.extend(message.packObject('mp3') + message.packObject(2))
                msgbytes.extend(
                    message.packObject(0) +
                    message.packObject(NetworkIntType(fileinfo[2])) +
                    message.packObject(1) +
                    message.packObject(NetworkIntType(fileinfo[3]))
                )
                stream.extend(msgbytes)
            except Exception:
                log.addwarning(_("Found meta data that couldn't be encoded, possible corrupt file: '%(file)s' has a bitrate of %(bitrate)s kbs and a length of %(length)s seconds" % {
                    'file': fileinfo[0],
                    'bitrate': fileinfo[2],
                    'length': fileinfo[3]
                }))
                stream.extend(message.packObject('') + message.packObject(0))
        else:
            stream.extend(message.packObject('') + message.packObject(0))

        return stream