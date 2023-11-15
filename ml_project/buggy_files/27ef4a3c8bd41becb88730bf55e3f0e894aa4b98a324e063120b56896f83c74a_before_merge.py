    def create_tar_oio_stream(self, entry, range_):
        """Extract data from entry from object"""
        mem = ""
        name = entry['name']

        if range_[0] < entry['hdr_blocks']:
            tar = OioTarEntry(self.storage, self.acct, self.container, name)

            for bl in xrange(entry['hdr_blocks']):
                if bl >= range_[0] and bl <= range_[1]:
                    mem += tar.buf[bl * BLOCKSIZE:bl * BLOCKSIZE + BLOCKSIZE]
            range_ = (entry['hdr_blocks'], range_[1])

        if range_[0] > range_[1]:
            return mem

        # for sanity, shift ranges
        range_ = (range_[0] - entry['hdr_blocks'],
                  range_[1] - entry['hdr_blocks'])

        # compute needed padding data
        nb_blocks, remainder = divmod(entry['size'], BLOCKSIZE)

        start = range_[0] * BLOCKSIZE
        last = False
        if remainder > 0 and nb_blocks == range_[1]:
            last = True
            end = entry['size'] - 1
        else:
            end = range_[1] * BLOCKSIZE + BLOCKSIZE - 1

        if entry['slo']:
            # we have now to compute which block(s) we need to read
            slo_start = 0
            for part in entry['slo']:
                if start > part['bytes']:
                    start -= part['bytes']
                    end -= part['bytes']
                    continue
                slo_end = min(end, part['bytes'])
                slo_start = start

                cnt, path = part['name'].strip('/').split('/', 1)
                _, data = self.storage.object_fetch(
                    self.acct, cnt, path, ranges=[(slo_start, slo_end)])
                mem += "".join(data)

                start = max(0, start - part['bytes'])
                end -= part['bytes']
                if end <= 0:
                    break
        else:
            _, data = self.storage.object_fetch(
                self.acct, self.container, name, ranges=[(start, end)])
            mem += "".join(data)

        if last:
            mem += NUL * (BLOCKSIZE - remainder)

        if not mem:
            self.logger.error("no data extracted")
        if divmod(len(mem), BLOCKSIZE)[1]:
            self.logger.error("data written does not match blocksize")
        return mem