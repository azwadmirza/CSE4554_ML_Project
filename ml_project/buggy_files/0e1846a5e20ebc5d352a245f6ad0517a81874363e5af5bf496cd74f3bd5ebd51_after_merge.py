    async def get_node_info(cls, node_id):
        node_physical_stats = dict(
            DataSource.node_physical_stats.get(node_id, {}))
        node_stats = dict(DataSource.node_stats.get(node_id, {}))
        node = DataSource.nodes.get(node_id, {})
        node_ip = DataSource.node_id_to_ip.get(node_id)
        # Merge node log count information into the payload
        log_info = DataSource.ip_and_pid_to_logs.get(node_ip, {})
        node_log_count = 0
        for entries in log_info.values():
            node_log_count += len(entries)
        error_info = DataSource.ip_and_pid_to_errors.get(node_ip, {})
        node_err_count = 0
        for entries in error_info.values():
            node_err_count += len(entries)

        node_stats.pop("coreWorkersStats", None)

        view_data = node_stats.get("viewData", [])
        ray_stats = cls._extract_view_data(
            view_data,
            {"object_store_used_memory", "object_store_available_memory"})

        node_info = node_physical_stats
        # Merge node stats to node physical stats under raylet
        node_info["raylet"] = node_stats
        node_info["raylet"].update(ray_stats)

        # Merge GcsNodeInfo to node physical stats
        node_info["raylet"].update(node)
        # Merge actors to node physical stats
        node_info["actors"] = await cls.get_node_actors(node_id)
        # Update workers to node physical stats
        node_info["workers"] = DataSource.node_workers.get(node_id, [])
        node_info["logCount"] = node_log_count
        node_info["errorCount"] = node_err_count
        await GlobalSignals.node_info_fetched.send(node_info)

        return node_info