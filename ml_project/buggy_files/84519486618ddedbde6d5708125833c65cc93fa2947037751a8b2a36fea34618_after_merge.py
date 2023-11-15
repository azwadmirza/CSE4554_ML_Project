    async def _get_actor(actor):
        actor = dict(actor)
        worker_id = actor["address"]["workerId"]
        core_worker_stats = DataSource.core_worker_stats.get(worker_id, {})
        actor_constructor = core_worker_stats.get("actorTitle",
                                                  "Unknown actor constructor")
        actor["actorConstructor"] = actor_constructor
        actor.update(core_worker_stats)

        # TODO(fyrestone): remove this, give a link from actor
        # info to worker info in front-end.
        node_id = actor["address"]["rayletId"]
        pid = core_worker_stats.get("pid")
        node_physical_stats = DataSource.node_physical_stats.get(node_id, {})
        actor_process_stats = None
        actor_process_gpu_stats = None
        if pid:
            for process_stats in node_physical_stats.get("workers", []):
                if process_stats["pid"] == pid:
                    actor_process_stats = process_stats
                    break

            for gpu_stats in node_physical_stats.get("gpus", []):
                for process in gpu_stats.get("processes", []):
                    if process["pid"] == pid:
                        actor_process_gpu_stats = gpu_stats
                        break
                if actor_process_gpu_stats is not None:
                    break

        actor["gpus"] = actor_process_gpu_stats
        actor["processStats"] = actor_process_stats

        return actor