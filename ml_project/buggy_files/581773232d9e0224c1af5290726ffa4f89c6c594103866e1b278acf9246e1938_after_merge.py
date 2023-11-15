    def __init__(self, *, plugin: 'HW_PluginBase'):
        assert_runs_in_hwd_thread()
        self.plugin = plugin