    def copy_to(self, session_id, data_keys, device_order, ensure=True, pin_token=None):
        device_order = self._normalize_devices(device_order)
        existing_devs = self._manager_ref.get_data_locations(session_id, data_keys)
        data_sizes = self._manager_ref.get_data_sizes(session_id, data_keys)

        device_to_keys = defaultdict(list)
        device_total_size = defaultdict(lambda: 0)
        lift_reqs = defaultdict(list)
        for k, devices, size in zip(data_keys, existing_devs, data_sizes):
            if not devices or not size:
                err_msg = 'Data key (%s, %s) not exist, proc_id=%s' % (session_id, k, self.proc_id)
                return promise.finished(*build_exc_info(KeyError, err_msg), _accept=False)

            target = next((d for d in device_order if d in devices), None)
            if target is not None:
                lift_reqs[target].append(k)
            else:
                max_device = max(devices)
                device_to_keys[max_device].append(k)
                device_total_size[max_device] += size

        for target, data_keys in lift_reqs.items():
            handler = self.get_storage_handler(target)
            if getattr(handler, '_spillable', False):
                handler.lift_data_keys(session_id, data_keys)
        if not device_to_keys:
            return promise.finished()

        def _action(src_handler, h, keys):
            return h.load_from(session_id, keys, src_handler, pin_token=pin_token)

        def _handle_exc(keys, *exc):
            existing = self._manager_ref.get_data_locations(session_id, keys)
            for devices in existing:
                if not any(d for d in device_order if d in devices):
                    raise exc[1].with_traceback(exc[2]) from None

        promises = []
        for d in device_to_keys.keys():
            action = functools.partial(_action, self.get_storage_handler(d))
            keys = device_to_keys[d]
            total_size = device_total_size[d]
            promises.append(
                self._do_with_spill(action, keys, total_size, device_order, ensure=ensure)
                    .catch(functools.partial(_handle_exc, keys))
            )
        return promise.all_(promises)