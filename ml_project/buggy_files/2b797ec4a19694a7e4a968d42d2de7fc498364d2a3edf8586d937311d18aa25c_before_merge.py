    def get_measurement(self):
        """ Gets the rpm """
        pi = pigpio.pi()
        try:
            read_rpm = ReadRPM(
                pi, self.pin, self.weighting, self.rpm_pulses_per_rev)
            rpm = read_rpm.RPM()
            if rpm:
                return int(rpm + 0.5)
        finally:
            p.cancel()
            pi.stop()
        return None