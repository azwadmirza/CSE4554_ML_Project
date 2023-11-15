    def _prepare_result(self):
        tmp = []

        for server in self.hcloud_server_info:
            if server is not None:
                image = None if server.image is None else to_native(server.image.name)
                tmp.append({
                    "id": to_native(server.id),
                    "name": to_native(server.name),
                    "ipv4_address": to_native(server.public_net.ipv4.ip),
                    "ipv6": to_native(server.public_net.ipv6.ip),
                    "image": image,
                    "server_type": to_native(server.server_type.name),
                    "datacenter": to_native(server.datacenter.name),
                    "location": to_native(server.datacenter.location.name),
                    "rescue_enabled": server.rescue_enabled,
                    "backup_window": to_native(server.backup_window),
                    "labels": server.labels,
                    "status": to_native(server.status),
                    "delete_protection": server.protection["delete"],
                    "rebuild_protection": server.protection["rebuild"],
                })
        return tmp