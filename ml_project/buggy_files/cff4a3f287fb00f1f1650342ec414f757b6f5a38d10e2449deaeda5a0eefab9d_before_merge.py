    def getByteStream(self, fileinfo):

        message = slskmessages.SlskMessage()

        stream = bytes([1]) + message.packObject(fileinfo[0]) + message.packObject(NetworkLongLongType(fileinfo[1]))
        if fileinfo[2] is not None:
            try:
                msgbytes = b''
                msgbytes += message.packObject('mp3') + message.packObject(3)
                msgbytes += (
                    message.packObject(0) +
                    message.packObject(NetworkIntType(fileinfo[2][0])) +
                    message.packObject(1) +
                    message.packObject(NetworkIntType(fileinfo[3])) +
                    message.packObject(2) +
                    message.packObject(NetworkIntType(fileinfo[2][1]))
                )
                stream += msgbytes
            except Exception:
                log.addwarning(_("Found meta data that couldn't be encoded, possible corrupt file: '%(file)s' has a bitrate of %(bitrate)s kbs, a length of %(length)s seconds and a VBR of %(vbr)s" % {
                    'file': fileinfo[0],
                    'bitrate': fileinfo[2][0],
                    'length': fileinfo[3],
                    'vbr': fileinfo[2][1]
                }))
                stream += message.packObject('') + message.packObject(0)
        else:
            stream += message.packObject('') + message.packObject(0)

        return stream