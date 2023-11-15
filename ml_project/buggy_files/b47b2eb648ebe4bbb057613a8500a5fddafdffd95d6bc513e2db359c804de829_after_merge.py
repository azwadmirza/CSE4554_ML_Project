    def network_stats(self):
        """Return a dictionary containing a summary of the Dot11
        elements fields
        """
        summary = {}
        crypto = set()
        p = self.payload
        while isinstance(p, Dot11Elt):
            if p.ID == 0:
                summary["ssid"] = plain_str(p.info)
            elif p.ID == 3:
                summary["channel"] = ord(p.info)
            elif isinstance(p, Dot11EltRates):
                summary["rates"] = p.rates
            elif isinstance(p, Dot11EltRSN):
                crypto.add("WPA2")
            elif p.ID == 221:
                if isinstance(p, Dot11EltMicrosoftWPA) or \
                        p.info.startswith(b'\x00P\xf2\x01\x01\x00'):
                    crypto.add("WPA")
            p = p.payload
        if not crypto:
            if self.cap.privacy:
                crypto.add("WEP")
            else:
                crypto.add("OPN")
        summary["crypto"] = crypto
        return summary