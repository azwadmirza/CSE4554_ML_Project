    def get_mount_facts(self):
        uuids = dict()
        self.facts['mounts'] = []
        bind_mounts = []
        findmntPath = self.module.get_bin_path("findmnt")
        if findmntPath:
            rc, out, err = self.module.run_command("%s -lnur" % ( findmntPath ), use_unsafe_shell=True)
            if rc == 0:
                # find bind mounts, in case /etc/mtab is a symlink to /proc/mounts
                for line in out.split('\n'):
                    fields = line.rstrip('\n').split()
                    if(len(fields) < 2):
                        continue
                    if(re.match(".*\]",fields[1])):
                        bind_mounts.append(fields[0])

        mtab = get_file_content('/etc/mtab', '')
        for line in mtab.split('\n'):
            fields = line.rstrip('\n').split()
            if fields[0].startswith('/') or ':/' in fields[0]:
                if(fields[2] != 'none'):
                    size_total, size_available = self._get_mount_size_facts(fields[1])
                    if fields[0] in uuids:
                        uuid = uuids[fields[0]]
                    else:
                        uuid = 'NA'
                        lsblkPath = self.module.get_bin_path("lsblk")
                        if lsblkPath:
                            rc, out, err = self.module.run_command("%s -ln --output UUID %s" % (lsblkPath, fields[0]), use_unsafe_shell=True)

                            if rc == 0:
                                uuid = out.strip()
                                uuids[fields[0]] = uuid

                    if fields[1] in bind_mounts:
                        # only add if not already there, we might have a plain /etc/mtab
                        if not re.match(".*bind.*", fields[3]):
                            fields[3] += ",bind"

                    self.facts['mounts'].append(
                        {'mount': fields[1],
                         'device':fields[0],
                         'fstype': fields[2],
                         'options': fields[3],
                         # statvfs data
                         'size_total': size_total,
                         'size_available': size_available,
                         'uuid': uuid,
                         })