    def on_tunnel_remove(self, subject, change_type, tunnel, candidate):
        self.onActivity("Tunnel removed with: [Up = " + str(tunnel.bytes_up) +
                        " bytes | Down = " + str(tunnel.bytes_down) + " bytes]")