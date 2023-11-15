    def collect_status(self):
        """
        Collect worker status and write to kvstore
        """
        meta_dict = dict()
        try:
            if not self._upload_status:
                return

            cpu_percent = resource.cpu_percent()
            disk_io = resource.disk_io_usage()
            net_io = resource.net_io_usage()
            if cpu_percent is None or disk_io is None or net_io is None:
                return
            hw_metrics = dict()
            hw_metrics['cpu'] = max(0.0, resource.cpu_count() - cpu_percent / 100.0)
            hw_metrics['cpu_used'] = cpu_percent / 100.0
            hw_metrics['cpu_total'] = resource.cpu_count()

            cuda_info = resource.cuda_info() if self._with_gpu else None
            if cuda_info:
                hw_metrics['cuda'] = cuda_info.gpu_count
                hw_metrics['cuda_total'] = cuda_info.gpu_count

            hw_metrics['disk_read'] = disk_io[0]
            hw_metrics['disk_write'] = disk_io[1]
            hw_metrics['net_receive'] = net_io[0]
            hw_metrics['net_send'] = net_io[1]

            iowait = resource.iowait()
            if iowait is not None:
                hw_metrics['iowait'] = iowait

            mem_stats = resource.virtual_memory()
            hw_metrics['memory'] = int(mem_stats.available)

            hw_metrics['memory_used'] = int(mem_stats.used)
            hw_metrics['memory_total'] = int(mem_stats.total)

            cache_allocations = self._status_ref.get_cache_allocations()
            cache_total = cache_allocations.get('total', 0)
            hw_metrics['cached_total'] = int(cache_total)
            hw_metrics['cached_hold'] = int(cache_allocations.get('hold', 0))

            mem_quota_allocations = self._status_ref.get_mem_quota_allocations()
            mem_quota_total = mem_quota_allocations.get('total', 0)
            mem_quota_allocated = mem_quota_allocations.get('allocated', 0)
            if not mem_quota_allocations:
                hw_metrics['mem_quota'] = hw_metrics['memory']
                hw_metrics['mem_quota_used'] = hw_metrics['memory_used']
                hw_metrics['mem_quota_total'] = hw_metrics['memory_total']
                hw_metrics['mem_quota_hold'] = 0
            else:
                hw_metrics['mem_quota'] = int(mem_quota_total - mem_quota_allocated) or hw_metrics['memory']
                hw_metrics['mem_quota_used'] = int(mem_quota_allocated)
                hw_metrics['mem_quota_total'] = int(mem_quota_total)
                hw_metrics['mem_quota_hold'] = int(mem_quota_allocations.get('hold', 0))

            if options.worker.spill_directory:
                if isinstance(options.worker.spill_directory, str):
                    spill_dirs = options.worker.spill_directory.split(':')
                else:
                    spill_dirs = options.worker.spill_directory
                if spill_dirs and 'disk_stats' not in hw_metrics:
                    hw_metrics['disk_stats'] = dict()
                disk_stats = hw_metrics['disk_stats']

                agg_disk_used = agg_disk_total = 0.0
                agg_inode_used = agg_inode_total = 0
                for spill_dir in spill_dirs:
                    if not os.path.exists(spill_dir):
                        continue
                    if spill_dir not in disk_stats:
                        disk_stats[spill_dir] = dict()

                    disk_usage = resource.disk_usage(spill_dir)
                    disk_stats[spill_dir]['disk_total'] = disk_usage.total
                    agg_disk_total += disk_usage.total
                    disk_stats[spill_dir]['disk_used'] = disk_usage.used
                    agg_disk_used += disk_usage.used

                    vfs_stat = os.statvfs(spill_dir)
                    disk_stats[spill_dir]['inode_total'] = vfs_stat.f_files
                    agg_inode_total += vfs_stat.f_files
                    disk_stats[spill_dir]['inode_used'] = vfs_stat.f_files - vfs_stat.f_favail
                    agg_inode_used += vfs_stat.f_files - vfs_stat.f_favail
                hw_metrics['disk_used'] = agg_disk_used
                hw_metrics['disk_total'] = agg_disk_total
                hw_metrics['inode_used'] = agg_inode_used
                hw_metrics['inode_total'] = agg_inode_total

            cuda_card_stats = resource.cuda_card_stats() if self._with_gpu else None
            if cuda_card_stats:
                hw_metrics['cuda_stats'] = [dict(
                    product_name=stat.product_name,
                    gpu_usage=stat.gpu_usage,
                    temperature=stat.temperature,
                    fb_memory_total=stat.fb_mem_info.total,
                    fb_memory_used=stat.fb_mem_info.used,
                ) for stat in cuda_card_stats]

            meta_dict = dict()
            meta_dict['hardware'] = hw_metrics
            meta_dict['update_time'] = time.time()
            meta_dict['stats'] = dict()
            meta_dict['slots'] = dict()

            status_data = self._status_ref.get_stats()
            for k, v in status_data.items():
                meta_dict['stats'][k] = v

            slots_data = self._status_ref.get_slots()
            for k, v in slots_data.items():
                meta_dict['slots'][k] = v

            meta_dict['progress'] = self._status_ref.get_progress()
            meta_dict['details'] = gather_node_info()

            if options.vineyard.socket:  # pragma: no cover
                import vineyard
                client = vineyard.connect(options.vineyard.socket)
                meta_dict['vineyard'] = {'instance_id': client.instance_id}

            self._resource_ref.set_worker_meta(self._endpoint, meta_dict)
        except Exception as ex:
            logger.error('Failed to save status: %s. repr(meta_dict)=%r', str(ex), meta_dict)
        finally:
            self.ref().collect_status(_tell=True, _delay=1)