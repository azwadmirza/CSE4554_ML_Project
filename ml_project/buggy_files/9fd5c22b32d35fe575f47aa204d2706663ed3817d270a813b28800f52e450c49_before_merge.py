    def stages(self) -> List[str]:
        """Experiment's stage names"""
        stages_keys = list(self.stages_config.keys())
        return stages_keys