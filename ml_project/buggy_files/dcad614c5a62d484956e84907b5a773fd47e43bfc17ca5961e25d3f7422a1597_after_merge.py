    def rssi(self):
        """Get the signal strength in dBm"""
        if isinstance(self.details, dict) and "props" in self.details:
            rssi = self.details["props"].get("RSSI", 0)  # Should not be set to 0...
        elif hasattr(self.details, "RawSignalStrengthInDBm"):
            rssi = self.details.RawSignalStrengthInDBm
        elif hasattr(self.details, "Properties"):
            rssi = {p.Key: p.Value for p in self.details.Properties}['System.Devices.Aep.SignalStrength']
        else:
            rssi = None
        return int(rssi) if rssi is not None else None