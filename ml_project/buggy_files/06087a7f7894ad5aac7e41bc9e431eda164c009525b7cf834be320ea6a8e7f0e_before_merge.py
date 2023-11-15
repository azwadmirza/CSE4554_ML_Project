    def dump_catapult_trace(self,
                            path,
                            task_info,
                            breakdowns=True,
                            task_dep=True,
                            obj_dep=True):
        """Dump task profiling information to a file.

        This information can be viewed as a timeline of profiling information
        by going to chrome://tracing in the chrome web browser and loading the
        appropriate file.

        Args:
            path: The filepath to dump the profiling information to.
            task_info: The task info to use to generate the trace. Should be
                the output of ray.global_state.task_profiles().
            breakdowns: Boolean indicating whether to break down the tasks into
                more fine-grained segments.
            task_dep: Boolean indicating whether or not task submission edges
                should be included in the trace.
            obj_dep: Boolean indicating whether or not object dependency edges
                should be included in the trace.
        """
        workers = self.workers()

        task_table = {}
        # TODO(ekl) reduce the number of RPCs here with MGET
        for task_id, _ in task_info.items():
            try:
                # TODO (hme): do something to correct slider here,
                # slider should be correct to begin with, though.
                task_table[task_id] = self.task_table(task_id)
            except Exception as e:
                print("Could not find task {}".format(task_id))

        # filter out tasks not in task_table
        task_info = {k: v for k, v in task_info.items() if k in task_table}

        start_time = None
        for info in task_info.values():
            task_start = min(self._get_times(info))
            if not start_time or task_start < start_time:
                start_time = task_start

        def micros(ts):
            return int(1e6 * ts)

        def micros_rel(ts):
            return micros(ts - start_time)

        seen_obj = {}

        full_trace = []
        for task_id, info in task_info.items():
            worker = workers[info["worker_id"]]
            task_t_info = task_table[task_id]

            # The total_info dictionary is what is displayed when selecting a
            # task in the timeline. We copy the task spec so that we don't
            # modify it in place since we will use the original values later.
            total_info = copy.copy(task_table[task_id]["TaskSpec"])
            total_info["Args"] = [
                oid.hex()
                if isinstance(oid, ray.local_scheduler.ObjectID) else oid
                for oid in task_t_info["TaskSpec"]["Args"]
            ]
            total_info["ReturnObjectIDs"] = [
                oid.hex() for oid in task_t_info["TaskSpec"]["ReturnObjectIDs"]
            ]
            total_info["LocalSchedulerID"] = task_t_info["LocalSchedulerID"]
            total_info["get_arguments"] = (
                info["get_arguments_end"] - info["get_arguments_start"])
            total_info["execute"] = (
                info["execute_end"] - info["execute_start"])
            total_info["store_outputs"] = (
                info["store_outputs_end"] - info["store_outputs_start"])
            total_info["function_name"] = info["function_name"]
            total_info["worker_id"] = info["worker_id"]

            parent_info = task_info.get(
                task_table[task_id]["TaskSpec"]["ParentTaskID"])
            worker = workers[info["worker_id"]]
            # The catapult trace format documentation can be found here:
            # https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/preview  # noqa: E501
            if breakdowns:
                if "get_arguments_end" in info:
                    get_args_trace = {
                        "cat":
                        "get_arguments",
                        "pid":
                        "Node " + worker["node_ip_address"],
                        "tid":
                        info["worker_id"],
                        "id":
                        task_id,
                        "ts":
                        micros_rel(info["get_arguments_start"]),
                        "ph":
                        "X",
                        "name":
                        info["function_name"] + ":get_arguments",
                        "args":
                        total_info,
                        "dur":
                        micros(info["get_arguments_end"] -
                               info["get_arguments_start"]),
                        "cname":
                        "rail_idle"
                    }
                    full_trace.append(get_args_trace)

                if "store_outputs_end" in info:
                    outputs_trace = {
                        "cat":
                        "store_outputs",
                        "pid":
                        "Node " + worker["node_ip_address"],
                        "tid":
                        info["worker_id"],
                        "id":
                        task_id,
                        "ts":
                        micros_rel(info["store_outputs_start"]),
                        "ph":
                        "X",
                        "name":
                        info["function_name"] + ":store_outputs",
                        "args":
                        total_info,
                        "dur":
                        micros(info["store_outputs_end"] -
                               info["store_outputs_start"]),
                        "cname":
                        "thread_state_runnable"
                    }
                    full_trace.append(outputs_trace)

                if "execute_end" in info:
                    execute_trace = {
                        "cat":
                        "execute",
                        "pid":
                        "Node " + worker["node_ip_address"],
                        "tid":
                        info["worker_id"],
                        "id":
                        task_id,
                        "ts":
                        micros_rel(info["execute_start"]),
                        "ph":
                        "X",
                        "name":
                        info["function_name"] + ":execute",
                        "args":
                        total_info,
                        "dur":
                        micros(info["execute_end"] - info["execute_start"]),
                        "cname":
                        "rail_animation"
                    }
                    full_trace.append(execute_trace)

            else:
                if parent_info:
                    parent_worker = workers[parent_info["worker_id"]]
                    parent_times = self._get_times(parent_info)
                    parent_profile = task_info.get(
                        task_table[task_id]["TaskSpec"]["ParentTaskID"])
                    parent = {
                        "cat":
                        "submit_task",
                        "pid":
                        "Node " + parent_worker["node_ip_address"],
                        "tid":
                        parent_info["worker_id"],
                        "ts":
                        micros_rel(parent_profile
                                   and parent_profile["get_arguments_start"]
                                   or start_time),
                        "ph":
                        "s",
                        "name":
                        "SubmitTask",
                        "args": {},
                        "id": (parent_info["worker_id"] +
                               str(micros(min(parent_times))))
                    }
                    full_trace.append(parent)

                    task_trace = {
                        "cat":
                        "submit_task",
                        "pid":
                        "Node " + worker["node_ip_address"],
                        "tid":
                        info["worker_id"],
                        "ts":
                        micros_rel(info["get_arguments_start"]),
                        "ph":
                        "f",
                        "name":
                        "SubmitTask",
                        "args": {},
                        "id":
                        (info["worker_id"] + str(micros(min(parent_times)))),
                        "bp":
                        "e",
                        "cname":
                        "olive"
                    }
                    full_trace.append(task_trace)

                task = {
                    "cat":
                    "task",
                    "pid":
                    "Node " + worker["node_ip_address"],
                    "tid":
                    info["worker_id"],
                    "id":
                    task_id,
                    "ts":
                    micros_rel(info["get_arguments_start"]),
                    "ph":
                    "X",
                    "name":
                    info["function_name"],
                    "args":
                    total_info,
                    "dur":
                    micros(info["store_outputs_end"] -
                           info["get_arguments_start"]),
                    "cname":
                    "thread_state_runnable"
                }
                full_trace.append(task)

            if task_dep:
                if parent_info:
                    parent_worker = workers[parent_info["worker_id"]]
                    parent_times = self._get_times(parent_info)
                    parent_profile = task_info.get(
                        task_table[task_id]["TaskSpec"]["ParentTaskID"])
                    parent = {
                        "cat":
                        "submit_task",
                        "pid":
                        "Node " + parent_worker["node_ip_address"],
                        "tid":
                        parent_info["worker_id"],
                        "ts":
                        micros_rel(parent_profile
                                   and parent_profile["get_arguments_start"]
                                   or start_time),
                        "ph":
                        "s",
                        "name":
                        "SubmitTask",
                        "args": {},
                        "id": (parent_info["worker_id"] +
                               str(micros(min(parent_times))))
                    }
                    full_trace.append(parent)

                    task_trace = {
                        "cat":
                        "submit_task",
                        "pid":
                        "Node " + worker["node_ip_address"],
                        "tid":
                        info["worker_id"],
                        "ts":
                        micros_rel(info["get_arguments_start"]),
                        "ph":
                        "f",
                        "name":
                        "SubmitTask",
                        "args": {},
                        "id":
                        (info["worker_id"] + str(micros(min(parent_times)))),
                        "bp":
                        "e"
                    }
                    full_trace.append(task_trace)

            if obj_dep:
                args = task_table[task_id]["TaskSpec"]["Args"]
                for arg in args:
                    # Don't visualize arguments that are not object IDs.
                    if isinstance(arg, ray.local_scheduler.ObjectID):
                        object_info = self._object_table(arg)
                        # Don't visualize objects that were created by calls to
                        # put.
                        if not object_info["IsPut"]:
                            if arg not in seen_obj:
                                seen_obj[arg] = 0
                            seen_obj[arg] += 1
                            owner_task = self._object_table(arg)["TaskID"]
                            if owner_task in task_info:
                                owner_worker = (workers[task_info[owner_task][
                                    "worker_id"]])
                                # Adding/subtracting 2 to the time associated
                                # with the beginning/ending of the flow event
                                # is necessary to make the flow events show up
                                # reliably. When these times are exact, this is
                                # presumably an edge case, and catapult doesn't
                                # recognize that there is a duration event at
                                # that exact point in time that the flow event
                                # should be bound to. This issue is solved by
                                # adding the 2 ms to the start/end time of the
                                # flow event, which guarantees overlap with the
                                # duration event that it's associated with, and
                                # the flow event therefore always gets drawn.
                                owner = {
                                    "cat":
                                    "obj_dependency",
                                    "pid": ("Node " +
                                            owner_worker["node_ip_address"]),
                                    "tid":
                                    task_info[owner_task]["worker_id"],
                                    "ts":
                                    micros_rel(task_info[owner_task]
                                               ["store_outputs_end"]) - 2,
                                    "ph":
                                    "s",
                                    "name":
                                    "ObjectDependency",
                                    "args": {},
                                    "bp":
                                    "e",
                                    "cname":
                                    "cq_build_attempt_failed",
                                    "id":
                                    "obj" + str(arg) + str(seen_obj[arg])
                                }
                                full_trace.append(owner)

                            dependent = {
                                "cat": "obj_dependency",
                                "pid": "Node " + worker["node_ip_address"],
                                "tid": info["worker_id"],
                                "ts":
                                micros_rel(info["get_arguments_start"]) + 2,
                                "ph": "f",
                                "name": "ObjectDependency",
                                "args": {},
                                "cname": "cq_build_attempt_failed",
                                "bp": "e",
                                "id": "obj" + str(arg) + str(seen_obj[arg])
                            }
                            full_trace.append(dependent)

        print("Creating JSON {}/{}".format(len(full_trace), len(task_info)))
        with open(path, "w") as outfile:
            json.dump(full_trace, outfile)