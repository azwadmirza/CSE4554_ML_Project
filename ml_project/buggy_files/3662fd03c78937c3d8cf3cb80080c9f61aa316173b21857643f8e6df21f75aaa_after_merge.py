    def get_measurement(self):
        """ Gets the pwm """
        try:
            pi = pigpio.pi()
            read_pwm = ReadPWM(pi, self.pin, self.weighting)
        except Exception:
            return

        try:
            frequency = read_pwm.frequency()
            pulse_width = read_pwm.pulse_width()
            duty_cycle = read_pwm.duty_cycle()
            return frequency, int(pulse_width + 0.5), duty_cycle
        finally:
            read_pwm.cancel()
            pi.stop()