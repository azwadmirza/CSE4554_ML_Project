    def _find_fld(self):
        """Returns the Field subclass to be used, depending on the Packet
instance, or the default subclass.

DEV: since the Packet instance is not provided, we have to use a hack
to guess it. It should only be used if you cannot provide the current
Packet instance (for example, because of the current Scapy API).

If you have the current Packet instance, use ._find_fld_pkt_val() (if
the value to set is also known) of ._find_fld_pkt() instead.

        """
        # Hack to preserve current Scapy API
        # See https://stackoverflow.com/a/7272464/3223422
        frame = inspect.currentframe().f_back.f_back
        while frame is not None:
            try:
                pkt = frame.f_locals['self']
            except KeyError:
                pass
            else:
                if not pkt.default_fields:
                    # Packet not initialized
                    return self.dflt
                if isinstance(pkt, tuple(self.dflt.owners)):
                    return self._find_fld_pkt(pkt)
            frame = frame.f_back
        return self.dflt