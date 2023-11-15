    def convert_discovered_torrents(self):
        offset = 0
        # Reflect conversion state
        with db_session:
            v = self.mds.MiscData.get_for_update(name=CONVERSION_FROM_72_DISCOVERED)
            if v:
                offset = orm.count(
                    g for g in self.mds.TorrentMetadata if
                    g.status == LEGACY_ENTRY and g.metadata_type == REGULAR_TORRENT)
                v.set(value=CONVERSION_STARTED)
            else:
                self.mds.MiscData(name=CONVERSION_FROM_72_DISCOVERED, value=CONVERSION_STARTED)

        start_time = datetime.datetime.utcnow()
        batch_size = 100
        total_to_convert = self.get_old_torrents_count()

        reference_timedelta = datetime.timedelta(milliseconds=1000)
        start = 0 + offset
        elapsed = 1
        while start < total_to_convert:
            batch = self.get_old_torrents(batch_size=batch_size, offset=start)
            if not batch or self.shutting_down:
                break

            end = start + len(batch)

            batch_start_time = datetime.datetime.now()
            try:
                with db_session:
                    for (t, _) in batch:
                        try:
                            self.mds.TorrentMetadata.add_ffa_from_dict(t)
                        except (TransactionIntegrityError, CacheIndexError):
                            pass
            except (TransactionIntegrityError, CacheIndexError):
                pass
            batch_end_time = datetime.datetime.now() - batch_start_time

            elapsed = (datetime.datetime.utcnow() - start_time).total_seconds()
            yield self.update_convert_progress(start, total_to_convert, elapsed)
            target_coeff = (batch_end_time.total_seconds() / reference_timedelta.total_seconds())
            if len(batch) == batch_size:
                # Adjust batch size only for full batches
                if target_coeff < 0.8:
                    batch_size += batch_size
                elif target_coeff > 1.1:
                    batch_size = int(float(batch_size) / target_coeff)
                # we want to guarantee that at least some entries will go through
                batch_size = batch_size if batch_size > 10 else 10
            self._logger.info("Converted old torrents: %i/%i %f ",
                              start + batch_size, total_to_convert, float(batch_end_time.total_seconds()))
            start = end

        with db_session:
            v = self.mds.MiscData.get_for_update(name=CONVERSION_FROM_72_DISCOVERED)
            v.value = CONVERSION_FINISHED

        yield self.update_convert_total(start, elapsed)