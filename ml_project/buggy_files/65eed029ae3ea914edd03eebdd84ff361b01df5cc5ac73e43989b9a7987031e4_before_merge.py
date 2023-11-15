    def __init__(self):
        """Initialize a Worker object."""
        # The functions field is a dictionary that maps a driver ID to a
        # dictionary of functions that have been registered for that driver
        # (this inner dictionary maps function IDs to a tuple of the function
        # name and the function itself). This should only be used on workers
        # that execute remote functions.
        self.functions = collections.defaultdict(lambda: {})
        # The function_properties field is a dictionary that maps a driver ID
        # to a dictionary of functions that have been registered for that
        # driver (this inner dictionary maps function IDs to a tuple of the
        # number of values returned by that function, the number of CPUs
        # required by that function, and the number of GPUs required by that
        # function). This is used when submitting a function (which can be done
        # both on workers and on drivers).
        self.function_properties = collections.defaultdict(lambda: {})
        # This is a dictionary mapping driver ID to a dictionary that maps
        # remote function IDs for that driver to a counter of the number of
        # times that remote function has been executed on this worker. The
        # counter is incremented every time the function is executed on this
        # worker. When the counter reaches the maximum number of executions
        # allowed for a particular function, the worker is killed.
        self.num_task_executions = collections.defaultdict(lambda: {})
        self.connected = False
        self.mode = None
        self.cached_remote_functions_and_actors = []
        self.cached_functions_to_run = []
        self.fetch_and_register_actor = None
        self.make_actor = None
        self.actors = {}
        self.actor_task_counter = 0
        # The number of threads Plasma should use when putting an object in the
        # object store.
        self.memcopy_threads = 12
        # When the worker is constructed. Record the original value of the
        # CUDA_VISIBLE_DEVICES environment variable.
        self.original_gpu_ids = ray.utils.get_cuda_visible_devices()