def adapt_state_infos(state):
    return AdaptBlockInfo(
        insts=tuple(state.instructions),
        outgoing_phis=state.outgoing_phis,
        blockstack=state.blockstack_initial,
        active_try_block=state.find_initial_try_block(),
        outgoing_edgepushed=state.get_outgoing_edgepushed(),
    )