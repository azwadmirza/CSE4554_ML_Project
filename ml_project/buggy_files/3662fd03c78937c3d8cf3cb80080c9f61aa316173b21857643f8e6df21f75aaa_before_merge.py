    def get_measurement(self):
        """ Gets the pwm """
        pi = pigpio.pi()
        try:
            read_pwm = ReadPWM(pi, self.pin, self.weighting)
            frequency = read_pwm.frequency()
            pulse_width = read_pwm.pulse_width()
            duty_cycle = read_pwm.duty_cycle()
            return frequency, int(pulse_width + 0.5), duty_cycle
        finally:
            p.cancel()
            pi.stop()