    def __init__(self, scheduler_address, session_id, actor_ctx=None, **kw):
        from .worker.api import WorkerAPI
        from .scheduler.api import MetaAPI
        from .scheduler.resource import ResourceActor
        from .scheduler.utils import SchedulerClusterInfoActor
        from .actors import new_client

        self._session_id = session_id
        self._scheduler_address = scheduler_address
        self._worker_api = WorkerAPI()
        self._meta_api = MetaAPI(actor_ctx=actor_ctx, scheduler_endpoint=scheduler_address)

        self._running_mode = None
        self._actor_ctx = actor_ctx or new_client()
        self._cluster_info = self._actor_ctx.actor_ref(
            SchedulerClusterInfoActor.default_uid(), address=scheduler_address)
        is_distributed = self._cluster_info.is_distributed()
        self._running_mode = RunningMode.local_cluster \
            if not is_distributed else RunningMode.distributed
        self._resource_actor_ref = self._actor_ctx.actor_ref(
            ResourceActor.default_uid(), address=scheduler_address)

        self._address = kw.pop('address', None)
        self._extra_info = kw