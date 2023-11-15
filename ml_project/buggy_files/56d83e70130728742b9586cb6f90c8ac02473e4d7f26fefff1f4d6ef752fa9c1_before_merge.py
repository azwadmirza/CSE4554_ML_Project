def _text_circuit_drawer(circuit, filename=None, reverse_bits=False,
                         plot_barriers=True, justify=None, vertical_compression='high',
                         idle_wires=True, with_layout=True, fold=None, initial_state=True,
                         cregbundle=False):
    """Draws a circuit using ascii art.

    Args:
        circuit (QuantumCircuit): Input circuit
        filename (str): optional filename to write the result
        reverse_bits (bool): Rearrange the bits in reverse order.
        plot_barriers (bool): Draws the barriers when they are there.
        justify (str) : `left`, `right` or `none`. Defaults to `left`. Says how
                        the circuit should be justified.
        vertical_compression (string): `high`, `medium`, or `low`. It merges the
            lines so the drawing will take less vertical room. Default is `high`.
        idle_wires (bool): Include idle wires. Default is True.
        with_layout (bool): Include layout information, with labels on the physical
            layout. Default: True
        fold (int): Optional. Breaks the circuit drawing to this length. This
                    useful when the drawing does not fit in the console. If
                    None (default), it will try to guess the console width using
                    `shutil.get_terminal_size()`. If you don't want pagination
                   at all, set `fold=-1`.
        initial_state (bool): Optional. Adds |0> in the beginning of the line. Default: `True`.
        cregbundle (bool): Optional. If set True bundle classical registers. Only used by
            the ``text`` output. Default: ``False``.
    Returns:
        TextDrawing: An instances that, when printed, draws the circuit in ascii art.
    """
    qregs, cregs, ops = utils._get_layered_instructions(circuit,
                                                        reverse_bits=reverse_bits,
                                                        justify=justify,
                                                        idle_wires=idle_wires)
    if with_layout:
        layout = circuit._layout
    else:
        layout = None
    global_phase = circuit.global_phase if hasattr(circuit, 'global_phase') else None
    text_drawing = _text.TextDrawing(qregs, cregs, ops, layout=layout, initial_state=initial_state,
                                     cregbundle=cregbundle, global_phase=global_phase)
    text_drawing.plotbarriers = plot_barriers
    text_drawing.line_length = fold
    text_drawing.vertical_compression = vertical_compression

    if filename:
        text_drawing.dump(filename)
    return text_drawing