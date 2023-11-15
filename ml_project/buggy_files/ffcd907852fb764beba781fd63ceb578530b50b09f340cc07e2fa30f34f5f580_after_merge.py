    def parse_header(self):
        self.dm_version = iou.read_long(self.f, "big")
        if self.dm_version not in (3, 4):
            raise NotImplementedError(
                "Currently we only support reading DM versions 3 and 4 but "
                "this file "
                "seems to be version %s " % self.dm_version)
        filesizeB = self.read_l_or_q(self.f, "big")
        is_little_endian = iou.read_long(self.f, "big")

        _logger.info('DM version: %i', self.dm_version)
        _logger.info('size %i B', filesizeB)
        _logger.info('Is file Little endian? %s', bool(is_little_endian))
        if bool(is_little_endian):
            self.endian = 'little'
        else:
            self.endian = 'big'