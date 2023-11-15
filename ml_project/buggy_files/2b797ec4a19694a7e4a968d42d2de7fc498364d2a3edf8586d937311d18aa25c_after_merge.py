    def get_measurement(self):
        """ Gets the rpm """
        try:
            pi = pigpio.pi()
            read_rpm = ReadRPM(
                pi, self.pin, self.weighting, self.rpm_pulses_per_rev)
        except Exception:
            return 0

        try:
            rpm = read_rpm.RPM()
            if rpm:
                return int(rpm + 0.5)
        except Exception:
            logger.exception(1)
        finally:
            read_rpm.cancel()
            pi.stop()
        return 0