def beam_search(step,
                input,
                bos_id,
                eos_id,
                beam_size,
                max_length=500,
                name=None,
                num_results_per_sample=None):
    """
    Beam search is a heuristic search algorithm used in sequence generation.
    It explores a graph by expanding the most promising nodes in a limited set
    to maintain tractability.

    The example usage is:

    .. code-block:: python

        def rnn_step(input):
            last_time_step_output = memory(name='rnn', size=512)
            with mixed_layer(size=512, name='rnn') as simple_rnn:
                simple_rnn += full_matrix_projection(input)
                simple_rnn += last_time_step_output
            return simple_rnn

        generated_word_embedding = GeneratedInput(
                               size=target_dictionary_dim,
                               embedding_name="target_language_embedding",
                               embedding_size=word_vector_dim)

        beam_gen = beam_search(name="decoder",
                               step=rnn_step,
                               input=[StaticInput(encoder_last),
                                      generated_word_embedding],
                               bos_id=0,
                               eos_id=1,
                               beam_size=5)

    Please see the following demo for more details:

    - machine translation : demo/seqToseq/translation/gen.conf \
                            demo/seqToseq/seqToseq_net.py

    :param name: Name of the recurrent unit that generates sequences.
    :type name: base string
    :param step: A callable function that defines the calculation in a time
                 step, and it is applied to sequences with arbitrary length by
                 sharing a same set of weights.

                 You can refer to the first parameter of recurrent_group, or
                 demo/seqToseq/seqToseq_net.py for more details.
    :type step: callable
    :param input: Input data for the recurrent unit, which should include the
                  previously generated words as a GeneratedInput object.
    :type input: list
    :param bos_id: Index of the start symbol in the dictionary. The start symbol
                   is a special token for NLP task, which indicates the
                   beginning of a sequence. In the generation task, the start
                   symbol is essential, since it is used to initialize the RNN
                   internal state.
    :type bos_id: int
    :param eos_id: Index of the end symbol in the dictionary. The end symbol is
                   a special token for NLP task, which indicates the end of a
                   sequence. The generation process will stop once the end
                   symbol is generated, or a pre-defined max iteration number
                   is exceeded.
    :type eos_id: int
    :param max_length: Max generated sequence length.
    :type max_length: int
    :param beam_size: Beam search for sequence generation is an iterative search
                      algorithm. To maintain tractability, every iteration only
                      only stores a predetermined number, called the beam_size,
                      of the most promising next words. The greater the beam
                      size, the fewer candidate words are pruned.
    :type beam_size: int
    :param num_results_per_sample: Number of the generated results per input
                                  sequence. This number must always be less than
                                  beam size.
    :type num_results_per_sample: int
    :return: The generated word index.
    :rtype: LayerOutput
    """

    if num_results_per_sample is None:
        num_results_per_sample = beam_size
    if num_results_per_sample > beam_size:
        logger.warning("num_results_per_sample should be less than beam_size")

    if isinstance(input, StaticInput) or isinstance(input, BaseGeneratedInput):
        input = [input]

    generated_input_index = -1

    real_input = []
    for i, each_input in enumerate(input):
        assert isinstance(each_input, StaticInput) or isinstance(
            each_input, BaseGeneratedInput)
        if isinstance(each_input, BaseGeneratedInput):
            assert generated_input_index == -1
            generated_input_index = i
        else:
            real_input.append(each_input)

    assert generated_input_index != -1

    gipt = input[generated_input_index]
    assert isinstance(gipt, BaseGeneratedInput)

    gipt.bos_id = bos_id
    gipt.eos_id = eos_id

    def __real_step__(*args):
        eos_name = "__%s_eos_layer__" % name
        RecurrentLayerGroupSetGenerator(
            Generator(
                eos_layer_name=eos_name,
                max_num_frames=max_length,
                beam_size=beam_size,
                num_results_per_sample=num_results_per_sample))

        args = list(args)
        args.insert(generated_input_index, gipt.before_real_step())

        predict = gipt.after_real_step(step(*args))

        eos_layer(input=predict, eos_id=eos_id, name=eos_name)

        return predict

    tmp = recurrent_group(
        step=__real_step__,
        input=real_input,
        reverse=False,
        name=name,
        is_generating=True)

    return tmp