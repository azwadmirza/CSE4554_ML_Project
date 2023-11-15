    def get_mount_facts(self):
        self.facts['mounts'] = []

        bind_mounts = self._find_bind_mounts()
        uuids = self._lsblk_uuid()
        mtab_entries = self._mtab_entries()

        mounts = []
        for fields in mtab_entries:
            device, mount, fstype, options = fields[0], fields[1], fields[2], fields[3]

            if not device.startswith('/') and ':/' not in device:
                continue

            if fstype == 'none':
                continue

            size_total, size_available = self._get_mount_size_facts(mount)

            if mount in bind_mounts:
                # only add if not already there, we might have a plain /etc/mtab
                if not self.MTAB_BIND_MOUNT_RE.match(options):
                    options += ",bind"

            mount_info = {'mount': mount,
                          'device': device,
                          'fstype': fstype,
                          'options': options,
                          # statvfs data
                          'size_total': size_total,
                          'size_available': size_available,
                          'uuid': uuids.get(device, 'N/A')}

            mounts.append(mount_info)

        self.facts['mounts'] = mounts