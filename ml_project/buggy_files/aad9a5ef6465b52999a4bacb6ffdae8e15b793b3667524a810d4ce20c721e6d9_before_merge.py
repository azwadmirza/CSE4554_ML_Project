    def _prepare_result(self):
        return {
            "id": to_native(self.hcloud_server.id),
            "name": to_native(self.hcloud_server.name),
            "ipv4_address": to_native(self.hcloud_server.public_net.ipv4.ip),
            "ipv6": to_native(self.hcloud_server.public_net.ipv6.ip),
            "image": to_native(self.hcloud_server.image.name),
            "server_type": to_native(self.hcloud_server.server_type.name),
            "datacenter": to_native(self.hcloud_server.datacenter.name),
            "location": to_native(self.hcloud_server.datacenter.location.name),
            "rescue_enabled": self.hcloud_server.rescue_enabled,
            "backup_window": to_native(self.hcloud_server.backup_window),
            "labels": self.hcloud_server.labels,
            "delete_protection": self.hcloud_server.protection["delete"],
            "rebuild_protection": self.hcloud_server.protection["rebuild"],
            "status": to_native(self.hcloud_server.status),
        }