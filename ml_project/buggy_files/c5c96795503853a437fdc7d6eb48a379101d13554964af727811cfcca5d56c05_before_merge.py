    def initialize_values(self):
        """Set PID parameters"""
        pid = db_retrieve_table_daemon(PID, device_id=self.pid_id)
        self.is_activated = pid.is_activated
        self.is_held = pid.is_held
        self.is_paused = pid.is_paused
        self.pid_type = pid.pid_type
        self.measurement = pid.measurement
        self.method_id = pid.method_id
        self.direction = pid.direction
        self.raise_relay_id = pid.raise_relay_id
        self.raise_min_duration = pid.raise_min_duration
        self.raise_max_duration = pid.raise_max_duration
        self.raise_min_off_duration = pid.raise_min_off_duration
        self.lower_relay_id = pid.lower_relay_id
        self.lower_min_duration = pid.lower_min_duration
        self.lower_max_duration = pid.lower_max_duration
        self.lower_min_off_duration = pid.lower_min_off_duration
        self.Kp = pid.p
        self.Ki = pid.i
        self.Kd = pid.d
        self.integrator_min = pid.integrator_min
        self.integrator_max = pid.integrator_max
        self.period = pid.period
        self.max_measure_age = pid.max_measure_age
        self.default_set_point = pid.setpoint
        self.set_point = pid.setpoint

        sensor = db_retrieve_table_daemon(Sensor, device_id=pid.sensor_id)
        self.sensor_unique_id = sensor.unique_id
        self.sensor_duration = sensor.period

        return "success"