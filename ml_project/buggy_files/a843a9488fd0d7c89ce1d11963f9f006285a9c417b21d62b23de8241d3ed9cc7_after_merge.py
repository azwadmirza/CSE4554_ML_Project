    def ClusterInfo(self, request,
                    context=None) -> ray_client_pb2.ClusterInfoResponse:
        resp = ray_client_pb2.ClusterInfoResponse()
        resp.type = request.type
        if request.type == ray_client_pb2.ClusterInfoType.CLUSTER_RESOURCES:
            with disable_client_hook():
                resources = ray.cluster_resources()
            # Normalize resources into floats
            # (the function may return values that are ints)
            float_resources = {k: float(v) for k, v in resources.items()}
            resp.resource_table.CopyFrom(
                ray_client_pb2.ClusterInfoResponse.ResourceTable(
                    table=float_resources))
        elif request.type == \
                ray_client_pb2.ClusterInfoType.AVAILABLE_RESOURCES:
            with disable_client_hook():
                resources = ray.available_resources()
            # Normalize resources into floats
            # (the function may return values that are ints)
            float_resources = {k: float(v) for k, v in resources.items()}
            resp.resource_table.CopyFrom(
                ray_client_pb2.ClusterInfoResponse.ResourceTable(
                    table=float_resources))
        elif request.type == ray_client_pb2.ClusterInfoType.RUNTIME_CONTEXT:
            ctx = ray_client_pb2.ClusterInfoResponse.RuntimeContext()
            with disable_client_hook():
                rtc = ray.get_runtime_context()
                ctx.job_id = rtc.job_id.binary()
                ctx.node_id = rtc.node_id.binary()
                ctx.capture_client_tasks = \
                    rtc.should_capture_child_tasks_in_placement_group
            resp.runtime_context.CopyFrom(ctx)
        else:
            with disable_client_hook():
                resp.json = self._return_debug_cluster_info(request, context)
        return resp