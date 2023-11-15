    def stages(self) -> List[str]:
        """Experiment's stage names"""
        stages_keys = list(self.stages_config.keys())

        # Change start `stages_keys` if resume data were founded
        state_params = self.get_state_params(stages_keys[0])
        resume, resume_dir = [state_params.get(key, None)
                              for key in ["resume", "resume_dir"]]

        if resume_dir is not None:
            resume = resume_dir / str(resume)

        if resume is not None and Path(resume).is_file():
            checkpoint = utils.load_checkpoint(resume)
            start_stage = checkpoint["stage"]
            start_idx = stages_keys.index(start_stage)
            stages_keys = stages_keys[start_idx:]

        return stages_keys