    def get_ipv8_bootstrap_override(self):
        val = self.config['ipv8']['bootstrap_override']
        ip_port_tuple = (val[0], int(val[1])) if val else None
        return ip_port_tuple