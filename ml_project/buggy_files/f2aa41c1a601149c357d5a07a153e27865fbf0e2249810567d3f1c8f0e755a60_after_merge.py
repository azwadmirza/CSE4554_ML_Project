    def _visit_string(self, node):
        string = node.value.s
        if string.startswith('@nni.'):
            self.annotated = True
        else:
            return node  # not an annotation, ignore it

        if string.startswith('@nni.get_next_parameter'):
            deprecated_message = "'@nni.get_next_parameter' is deprecated in annotation due to inconvenience. " \
                                 "Please remove this line in the trial code."
            print_warning(deprecated_message)
            return ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()),
                                           args=[ast.Str(s='Get next parameter here...')], keywords=[]))

        if string.startswith('@nni.training_update'):
            return ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()),
                                           args=[ast.Str(s='Training update here...')], keywords=[]))

        if string.startswith('@nni.report_intermediate_result'):
            module = ast.parse(string[1:])
            arg = module.body[0].value.args[0]
            return ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()),
                                           args=[ast.Str(s='nni.report_intermediate_result: '), arg], keywords=[]))

        if string.startswith('@nni.report_final_result'):
            module = ast.parse(string[1:])
            arg = module.body[0].value.args[0]
            return ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()),
                                           args=[ast.Str(s='nni.report_final_result: '), arg], keywords=[]))

        if string.startswith('@nni.mutable_layers'):
            return parse_annotation_mutable_layers(string[1:], node.lineno)

        if string.startswith('@nni.variable') \
                or string.startswith('@nni.function_choice'):
            self.stack[-1] = string[1:]  # mark that the next expression is annotated
            return None

        raise AssertionError('Unexpected annotation function')