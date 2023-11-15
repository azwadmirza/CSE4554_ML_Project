    async def get_node_workers(cls, node_id):
        workers = []
        node_ip = DataSource.node_id_to_ip[node_id]
        node_logs = DataSource.ip_and_pid_to_logs.get(node_ip, {})
        node_errs = DataSource.ip_and_pid_to_errors.get(node_ip, {})
        node_physical_stats = DataSource.node_physical_stats.get(node_id, {})
        node_stats = DataSource.node_stats.get(node_id, {})
        # Merge coreWorkerStats (node stats) to workers (node physical stats)
        pid_to_worker_stats = {}
        pid_to_language = {}
        pid_to_job_id = {}
        for core_worker_stats in node_stats.get("coreWorkersStats", []):
            pid = core_worker_stats["pid"]
            pid_to_worker_stats.setdefault(pid, []).append(core_worker_stats)
            pid_to_language[pid] = core_worker_stats["language"]
            pid_to_job_id[pid] = core_worker_stats["jobId"]
        for worker in node_physical_stats.get("workers", []):
            worker = dict(worker)
            pid = worker["pid"]
            worker["logCount"] = len(node_logs.get(str(pid), []))
            worker["errorCount"] = len(node_errs.get(str(pid), []))
            worker["coreWorkerStats"] = pid_to_worker_stats.get(pid, [])
            worker["language"] = pid_to_language.get(
                pid, dashboard_consts.DEFAULT_LANGUAGE)
            worker["jobId"] = pid_to_job_id.get(
                pid, dashboard_consts.DEFAULT_JOB_ID)

            await GlobalSignals.worker_info_fetched.send(node_id, worker)

            workers.append(worker)
        return workers