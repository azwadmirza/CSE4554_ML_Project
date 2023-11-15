    def __call__(cls, *args, **kwargs):
        """A wrapper for LightningDataModule that:

            1. Runs user defined subclass's __init__
            2. Assures prepare_data() runs on rank 0
            3. Lets you check prepare_data and setup to see if they've been called
        """

        # Track prepare_data calls and make sure it runs on rank zero
        cls.prepare_data = track_data_hook_calls(rank_zero_only(cls.prepare_data))
        # Track setup calls
        cls.setup = track_data_hook_calls(cls.setup)

        # Get instance of LightningDataModule by mocking its __init__ via __call__
        obj = type.__call__(cls, *args, **kwargs)

        return obj