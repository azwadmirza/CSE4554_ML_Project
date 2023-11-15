    def logits(
            self,
            inputs,
            target=None,
            training=None
    ):
        if training:
            return self.decoder_obj._logits_training(
                inputs,
                target=tf.cast(target, dtype=tf.int32),
                training=training
            )
        else:
            return inputs