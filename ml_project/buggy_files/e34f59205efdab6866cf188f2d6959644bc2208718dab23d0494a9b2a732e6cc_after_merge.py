    def estimate_graph_finish_time(self, session_id, graph_key, calc_fetch=True, base_time=None):
        """
        Calc predictions for given chunk graph
        """
        session_graph_key = (session_id, graph_key)
        if session_graph_key not in self._graph_records:
            return
        graph_record = self._graph_records[session_graph_key]
        graph = graph_record.graph

        ops = set(type(c.op).__name__ for c in graph if not isinstance(c.op, Fetch))
        op_calc_key = ('calc_speed.' + list(ops)[0]) if len(ops) == 1 else None

        stats = defaultdict(lambda: dict(count=0))
        if self._status_ref:
            stats.update(self._status_ref.get_stats(['disk_read_speed', 'disk_write_speed',
                                                     'net_transfer_speed', op_calc_key]))

        if op_calc_key not in stats:
            return None
        if stats[op_calc_key]['count'] < options.optimize.min_stats_count:
            return None
        if abs(stats[op_calc_key]['count']) < 1e-6:
            return None

        input_size = 0
        net_size = 0
        disk_size = 0
        base_time = base_time or time.time()

        if calc_fetch:
            for c in graph:
                if not isinstance(c.op, Fetch):
                    break
                try:
                    data_size = calc_data_size(c)
                except (AttributeError, TypeError, ValueError):
                    data_size = 0
                input_size += data_size
                data_locations = self.storage_client.get_data_locations(session_id, [c.key])[0]
                if (0, DataStorageDevice.VINEYARD) in data_locations or \
                        (0, DataStorageDevice.SHARED_MEMORY) in data_locations:  # pragma: no cover
                    continue
                elif (0, DataStorageDevice.DISK) in data_locations:
                    disk_size += data_size
                else:
                    net_size += data_size

            if stats['net_transfer_speed']['count'] >= options.optimize.min_stats_count:
                base_time += net_size * 1.0 / stats['net_transfer_speed']['mean']
            if stats['disk_read_speed']['count'] >= options.optimize.min_stats_count:
                base_time += disk_size * 1.0 / stats['disk_read_speed']['mean']
            else:
                base_time += disk_size * 1.0 / options.optimize.default_disk_io_speed

        est_finish_time = base_time + input_size * 1.0 / stats[op_calc_key]['mean']

        graph_record.est_finish_time = est_finish_time
        self._status_ref.update_stats(dict(
            min_est_finish_time=min(rec.est_finish_time for rec in self._graph_records.values()),
            max_est_finish_time=max(rec.est_finish_time for rec in self._graph_records.values()),
        ), _tell=True, _wait=False)

        self.ref().estimate_graph_finish_time(session_id, graph_key, _tell=True, _delay=1)