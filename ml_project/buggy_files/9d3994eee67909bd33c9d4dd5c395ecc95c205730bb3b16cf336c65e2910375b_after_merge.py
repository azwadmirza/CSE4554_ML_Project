    def _register_log_path(self):
        if self.is_log_path_registered:
            return

        # register log path
        session_id = self.ctx.session_id
        tileable_op_key = self.op.tileable_op_key
        chunk_op_key = self.op.key
        worker_addr = self.ctx.get_local_address()
        log_path = self.log_path

        custom_log_meta = self.ctx.get_custom_log_meta_ref()
        custom_log_meta.record_custom_log_path(
            session_id, tileable_op_key, chunk_op_key,
            worker_addr, log_path)

        self.is_log_path_registered = True