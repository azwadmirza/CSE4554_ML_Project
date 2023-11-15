    def _message(self, message_action_kind, msg):
        if message_action_kind == "get":
            self.instance.logger.info("Waiting for a message to get...")
            if not bool(self.instance._Bot__source_queues):
                self.instance.logger.warning("Bot has no source queue.")
                return

            # Never pops from source to internal queue, thx to disabling brpoplpush operation.
            # However, we have to wait manually till there is the message in the queue.
            pl = self.instance._Bot__source_pipeline
            pl.pipe.brpoplpush = lambda source_q, inter_q, i: pl.pipe.lindex(source_q, -1)
            while not (pl.pipe.llen(pl.source_queue) or pl.pipe.llen(pl.internal_queue)):
                time.sleep(1)
            self.pprint(self.instance.receive_message())
        elif message_action_kind == "pop":
            self.instance.logger.info("Waiting for a message to pop...")
            self.pprint(self.instance.receive_message())
            self.instance.acknowledge_message()
        elif message_action_kind == "send":
            if not bool(self.instance._Bot__destination_queues):
                self.instance.logger.warning("Bot has no destination queues.")
                return
            if msg:
                msg = self.arg2msg(msg)
                self.instance.send_message(msg, auto_add=False)
                self.instance.logger.info("Message sent to output pipelines.")
            else:
                self.messageWizzard("Message missing!")