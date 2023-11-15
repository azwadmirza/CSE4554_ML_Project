def build_base_model(model_opt, fields, gpu, checkpoint=None):
    """
    Args:
        model_opt: the option loaded from checkpoint.
        fields: `Field` objects for the model.
        gpu(bool): whether to use gpu.
        checkpoint: the model gnerated by train phase, or a resumed snapshot
                    model from a stopped training.
    Returns:
        the NMTModel.
    """
    assert model_opt.model_type in ["text", "img", "audio"], \
        "Unsupported model type %s" % model_opt.model_type

    # for backward compatibility
    if model_opt.rnn_size != -1:
        model_opt.enc_rnn_size = model_opt.rnn_size
        model_opt.dec_rnn_size = model_opt.rnn_size

    # Build encoder.
    if model_opt.model_type == "text":
        src_fields = [f for n, f in fields['src']]
        src_emb = build_embeddings(model_opt, src_fields[0], src_fields[1:])
        encoder = build_encoder(model_opt, src_emb)
    elif model_opt.model_type == "img":
        # why is build_encoder not used here?
        # why is the model_opt.__dict__ check necessary?
        if "image_channel_size" not in model_opt.__dict__:
            image_channel_size = 3
        else:
            image_channel_size = model_opt.image_channel_size

        encoder = ImageEncoder(
            model_opt.enc_layers,
            model_opt.brnn,
            model_opt.enc_rnn_size,
            model_opt.dropout,
            image_channel_size
        )
    elif model_opt.model_type == "audio":
        encoder = AudioEncoder(
            model_opt.rnn_type,
            model_opt.enc_layers,
            model_opt.dec_layers,
            model_opt.brnn,
            model_opt.enc_rnn_size,
            model_opt.dec_rnn_size,
            model_opt.audio_enc_pooling,
            model_opt.dropout,
            model_opt.sample_rate,
            model_opt.window_size
        )

    # Build decoder.
    tgt_fields = [f for n, f in fields['tgt']]
    tgt_emb = build_embeddings(
        model_opt, tgt_fields[0], tgt_fields[1:], for_encoder=False)

    # Share the embedding matrix - preprocess with share_vocab required.
    if model_opt.share_embeddings:
        # src/tgt vocab should be the same if `-share_vocab` is specified.
        assert src_fields[0].vocab == tgt_fields[0].vocab, \
            "preprocess with -share_vocab if you use share_embeddings"

        tgt_emb.word_lut.weight = src_emb.word_lut.weight

    decoder = build_decoder(model_opt, tgt_emb)

    # Build NMTModel(= encoder + decoder).
    device = torch.device("cuda" if gpu else "cpu")
    model = onmt.models.NMTModel(encoder, decoder)

    # Build Generator.
    if not model_opt.copy_attn:
        if model_opt.generator_function == "sparsemax":
            gen_func = onmt.modules.sparse_activations.LogSparsemax(dim=-1)
        else:
            gen_func = nn.LogSoftmax(dim=-1)
        generator = nn.Sequential(
            nn.Linear(model_opt.dec_rnn_size, len(fields["tgt"][0][1].vocab)),
            gen_func
        )
        if model_opt.share_decoder_embeddings:
            generator[0].weight = decoder.embeddings.word_lut.weight
    else:
        vocab_size = len(fields["tgt"][0][1].vocab)
        pad_idx = fields["tgt"][0][1].vocab.stoi[fields["tgt"][0][1].pad_token]
        generator = CopyGenerator(model_opt.dec_rnn_size, vocab_size, pad_idx)

    # Load the model states from checkpoint or initialize them.
    if checkpoint is not None:
        # This preserves backward-compat for models using customed layernorm
        def fix_key(s):
            s = re.sub(r'(.*)\.layer_norm((_\d+)?)\.b_2',
                       r'\1.layer_norm\2.bias', s)
            s = re.sub(r'(.*)\.layer_norm((_\d+)?)\.a_2',
                       r'\1.layer_norm\2.weight', s)
            return s

        checkpoint['model'] = {fix_key(k): v
                               for k, v in checkpoint['model'].items()}
        # end of patch for backward compatibility

        model.load_state_dict(checkpoint['model'], strict=False)
        generator.load_state_dict(checkpoint['generator'], strict=False)
    else:
        if model_opt.param_init != 0.0:
            for p in model.parameters():
                p.data.uniform_(-model_opt.param_init, model_opt.param_init)
            for p in generator.parameters():
                p.data.uniform_(-model_opt.param_init, model_opt.param_init)
        if model_opt.param_init_glorot:
            for p in model.parameters():
                if p.dim() > 1:
                    xavier_uniform_(p)
            for p in generator.parameters():
                if p.dim() > 1:
                    xavier_uniform_(p)

        if hasattr(model.encoder, 'embeddings'):
            model.encoder.embeddings.load_pretrained_vectors(
                model_opt.pre_word_vecs_enc, model_opt.fix_word_vecs_enc)
        if hasattr(model.decoder, 'embeddings'):
            model.decoder.embeddings.load_pretrained_vectors(
                model_opt.pre_word_vecs_dec, model_opt.fix_word_vecs_dec)

    model.generator = generator
    model.to(device)

    return model