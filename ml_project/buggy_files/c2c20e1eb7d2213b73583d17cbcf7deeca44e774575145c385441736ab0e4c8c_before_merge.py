    def _check_len(self, pkt):
        """Check for odd packet length and pad according to Cisco spec.
        This padding is only used for checksum computation.  The original
        packet should not be altered."""
        if len(pkt) % 2:
            last_chr = pkt[-1]
            if last_chr <= b'\x80':
                return pkt[:-1] + b'\x00' + last_chr
            else:
                return pkt[:-1] + b'\xff' + chb(orb(last_chr) - 1)
        else:
            return pkt