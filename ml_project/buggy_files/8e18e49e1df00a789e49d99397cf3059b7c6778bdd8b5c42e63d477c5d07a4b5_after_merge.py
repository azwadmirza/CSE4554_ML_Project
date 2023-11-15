    def _process_packet(self, pkt):
        """Process each packet: matches the TCP seq/ack numbers
        to follow the TCP streams, and orders the fragments.
        """
        if self.app:
            # Special mode: Application layer. Use on top of TCP
            pay_class = pkt.__class__
            if not hasattr(pay_class, "tcp_reassemble"):
                # Being on top of TCP, we have no way of knowing
                # when a packet ends.
                return pkt
            self.data += bytes(pkt)
            pkt = pay_class.tcp_reassemble(self.data, self.metadata)
            if pkt:
                self.data = b""
                self.metadata = {}
                return pkt
            return

        from scapy.layers.inet import IP, TCP
        if not pkt or TCP not in pkt:
            return pkt
        pay = pkt[TCP].payload
        if isinstance(pay, (NoPayload, conf.padding_layer)):
            return pkt
        new_data = pay.original
        # Match packets by a uniqute TCP identifier
        seq = pkt[TCP].seq
        ident = pkt.sprintf(self.fmt)
        data, metadata = self.tcp_frags[ident]
        # Let's guess which class is going to be used
        if "pay_class" not in metadata:
            pay_class = pay.__class__
            if hasattr(pay_class, "tcp_reassemble"):
                tcp_reassemble = pay_class.tcp_reassemble
            else:
                # We can't know for sure when a packet ends.
                # Ignore.
                return pkt
            metadata["pay_class"] = pay_class
            metadata["tcp_reassemble"] = tcp_reassemble
        else:
            tcp_reassemble = metadata["tcp_reassemble"]
        # Get a relative sequence number for a storage purpose
        relative_seq = metadata.get("relative_seq", None)
        if relative_seq is None:
            relative_seq = metadata["relative_seq"] = seq - 1
        seq = seq - relative_seq
        # Add the data to the buffer
        # Note that this take care of retransmission packets.
        data.append(new_data, seq)
        # Check TCP FIN or TCP RESET
        if pkt[TCP].flags.F or pkt[TCP].flags.R:
            metadata["tcp_end"] = True

        # In case any app layer protocol requires it,
        # allow the parser to inspect TCP PSH flag
        if pkt[TCP].flags.P:
            metadata["tcp_psh"] = True
        # XXX TODO: check that no empty space is missing in the buffer.
        # XXX Currently, if a TCP fragment was missing, we won't notice it.
        packet = None
        if data.full():
            # Reassemble using all previous packets
            packet = tcp_reassemble(bytes(data), metadata)
        # Stack the result on top of the previous frames
        if packet:
            data.clear()
            metadata.clear()
            del self.tcp_frags[ident]
            pay.underlayer.remove_payload()
            if IP in pkt:
                pkt[IP].len = None
                pkt[IP].chksum = None
            return pkt / packet