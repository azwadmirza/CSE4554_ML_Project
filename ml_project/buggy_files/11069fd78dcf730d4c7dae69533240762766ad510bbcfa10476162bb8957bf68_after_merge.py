def _apply_tokenizer_to_states(tokenizer: Tokenizer, states: List[State]) -> None:
    """Split each user text into tokens and concatenate them again.

    Args:
        tokenizer: A tokenizer to tokenize the user messages.
        states: The states to be tokenized.
    """
    for state in states:
        if USER in state and TEXT in state[USER]:
            state[USER][TEXT] = " ".join(
                token.text
                for token in tokenizer.tokenize(
                    Message({TEXT: state[USER][TEXT]}), TEXT
                )
            )