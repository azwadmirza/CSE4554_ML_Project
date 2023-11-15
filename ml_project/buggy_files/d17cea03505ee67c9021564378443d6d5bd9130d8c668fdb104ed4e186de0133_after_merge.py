    def decoder_teacher_forcing(
            self,
            encoder_output,
            target=None,
            encoder_end_state=None
    ):
        # ================ Setup ================
        batch_size = tf.shape(encoder_output)[0]

        # Prepare target for decoding
        target_sequence_length = sequence_length_2D(target)
        start_tokens = tf.tile([self.GO_SYMBOL], [batch_size])
        end_tokens = tf.tile([self.END_SYMBOL], [batch_size])
        if self.is_timeseries:
            start_tokens = tf.cast(start_tokens, tf.float32)
            end_tokens = tf.cast(end_tokens, tf.float32)
        targets_with_go_and_eos = tf.concat([
            tf.expand_dims(start_tokens, 1),
            target,  # right now cast to tf.int32, fails if tf.int64
            tf.expand_dims(end_tokens, 1)], 1)
        target_sequence_length_with_eos = target_sequence_length + 1

        # Decoder Embeddings
        decoder_emb_inp = self.decoder_embedding(targets_with_go_and_eos)

        # Setting up decoder memory from encoder output
        if self.attention_mechanism is not None:
            encoder_sequence_length = sequence_length_3D(encoder_output)
            self.attention_mechanism.setup_memory(
                encoder_output,
                memory_sequence_length=encoder_sequence_length
            )

        decoder_initial_state = self.build_decoder_initial_state(
            batch_size,
            encoder_state=encoder_end_state,
            dtype=tf.float32
        )

        decoder = tfa.seq2seq.BasicDecoder(
            self.decoder_rnncell,
            sampler=self.sampler,
            output_layer=self.dense_layer
        )

        # BasicDecoderOutput
        outputs, final_state, generated_sequence_lengths = decoder(
            decoder_emb_inp,
            initial_state=decoder_initial_state,
            sequence_length=target_sequence_length_with_eos
        )

        logits = outputs.rnn_output
        # mask = tf.sequence_mask(
        #    generated_sequence_lengths,
        #    maxlen=tf.shape(logits)[1],
        #    dtype=tf.float32
        # )
        # logits = logits * mask[:, :, tf.newaxis]

        # append a trailing 0, useful for
        # those datapoints that reach maximum length
        # and don't have a eos at the end
        logits = tf.pad(
            logits,
            [[0, 0], [0, 1], [0, 0]]
        )

        return logits  # , outputs, final_state, generated_sequence_lengths