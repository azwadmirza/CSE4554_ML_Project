    def request_binding(self, guest_id, dst_ip, ssh_port, telnet_port):
        self.lock.acquire()
        try:
            # see if binding is already created
            if dst_ip in self.bindings:
                # increase connected
                self.bindings[guest_id][0] += 1

                return self.bindings[guest_id][1]._realPortNumber, self.bindings[guest_id][2]._realPortNumber

            else:
                nat_ssh = reactor.listenTCP(0, ServerFactory(dst_ip, ssh_port), interface='0.0.0.0')
                nat_telnet = reactor.listenTCP(0, ServerFactory(dst_ip, telnet_port), interface='0.0.0.0')
                self.bindings[guest_id] = [0, nat_ssh, nat_telnet]

                return nat_ssh._realPortNumber, nat_telnet._realPortNumber
        finally:
            self.lock.release()