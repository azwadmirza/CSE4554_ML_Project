    def __init__(self, prespawn_count, kernel_manager):
        self.kernel_manager = kernel_manager
        # Make sure we've got a int
        if not prespawn_count:
            prespawn_count = 0
        env = dict(os.environ)
        env['KERNEL_USERNAME'] = prespawn_username
        for _ in range(prespawn_count):
            self.kernel_manager.start_seeded_kernel(env=env)