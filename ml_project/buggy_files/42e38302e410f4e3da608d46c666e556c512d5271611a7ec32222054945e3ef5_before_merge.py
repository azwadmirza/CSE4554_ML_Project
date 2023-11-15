def adapt_state_infos(state):
    return AdaptBlockInfo(
        insts=tuple(state.instructions), outgoing_phis=state.outgoing_phis
    )