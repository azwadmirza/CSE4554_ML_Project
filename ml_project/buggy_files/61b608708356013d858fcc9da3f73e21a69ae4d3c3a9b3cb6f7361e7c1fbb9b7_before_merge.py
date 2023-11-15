    def find_dvs_by_uuid(self, uuid=None):
        dvs_obj = None
        if uuid is None:
            return dvs_obj

        dvswitches = get_all_objs(self.content, [vim.DistributedVirtualSwitch])
        for dvs in dvswitches:
            if dvs.uuid == uuid:
                dvs_obj = dvs
                break

        return dvs_obj