def build_snippet_ast(snippet_text):
    """Given a snippet string, return its abstract syntax tree (AST)."""
    snippet_text = codecs.decode(snippet_text, 'unicode_escape')
    tokens = tokenize(snippet_text)
    tokens += [Token('eof', '<eof>')]

    stack = [STARTING_RULE]

    current_ctx = (STARTING_RULE, None)
    current_args = []
    current_prefix = [STARTING_RULE]

    context_stack = []
    args_stack = []
    prefix_stack = []

    while len(stack) > 0:
        peek_token = tokens[0]
        current_rule = stack.pop(0)
        if current_rule in GRAMMAR:
            # A grammar production rule
            follow_predictions = PARSE_TABLE[current_rule]
            next_productions = []
            if peek_token.token in follow_predictions:
                next_productions = follow_predictions[peek_token.token]
            elif peek_token.value in follow_predictions:
                next_productions = follow_predictions[peek_token.value]
            else:
                raise SyntaxError('Syntax Error: Expected any of the following'
                                  ' characters: {0}, got {1}'.format(
                                      list(follow_predictions.keys()),
                                      peek_token
                                    ))
            current_prefix.pop(0)
            stack = next_productions + stack
            new_ctx = switch_context(current_rule, current_ctx, current_args,
                                     current_prefix, context_stack, args_stack,
                                     prefix_stack)
            (current_ctx, current_args, current_prefix,
             context_stack, args_stack, prefix_stack) = new_ctx
            current_prefix = next_productions + current_prefix
        else:
            # A terminal symbol
            if peek_token.token == current_rule:
                tokens.pop(0)
            elif peek_token.value == current_rule:
                tokens.pop(0)
            else:
                raise SyntaxError('Syntax Error: Expected {0}, got {1}'.format(
                    repr(peek_token.value), repr(current_rule)))

            current_name, _ = current_ctx
            add_to_args = True
            if current_name in IGNORE_TERMINALS:
                add_to_args = (peek_token.token not in
                               IGNORE_TERMINALS[current_name])

            if add_to_args:
                leaf = nodes.LeafNode(peek_token.token, peek_token.value)
                current_args.append(leaf)
            current_prefix.pop(0)

        if len(current_prefix) == 0:
            _, Node = current_ctx
            node = Node(*current_args)
            current_ctx = context_stack.pop(0)
            current_args = args_stack.pop(0)
            current_prefix = prefix_stack.pop(0)
            current_args.append(node)

    assert len(current_args) == 1
    return current_args[0]