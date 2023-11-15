    def _send_to_s3(self, force=False):
        """Copy in-memory batches to s3"""
        for table_name, batches in self._batches.items():
            if not force and len(batches) <= CACHE_SIZE:
                continue
            if table_name == SITE_VISITS_INDEX:
                out_str = '\n'.join([json.dumps(x) for x in batches])
                if not isinstance(out_str, six.binary_type):
                    out_str = out_str.encode('utf-8')
                fname = '%s/site_index/instance-%s-%s.json.gz' % (
                    self.dir, self._instance_id,
                    hashlib.md5(out_str).hexdigest()
                )
                self._write_str_to_s3(out_str, fname)
            else:
                if len(batches) == 0:
                    continue
                try:
                    table = pa.Table.from_batches(batches)
                    pq.write_to_dataset(
                        table, self._s3_bucket_uri % table_name,
                        filesystem=self._fs,
                        preserve_index=False,
                        partition_cols=['instance_id'],
                        compression='snappy',
                        flavor='spark'
                    )
                except (pa.lib.ArrowInvalid, EndpointConnectionError):
                    self.logger.error(
                        "Error while sending records for: %s" % table_name,
                        exc_info=True
                    )
                    pass
            self._batches[table_name] = list()