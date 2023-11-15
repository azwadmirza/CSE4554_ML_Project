def parse_annotation_mutable_layers(code, lineno, nas_mode):
    """Parse the string of mutable layers in annotation.
    Return a list of AST Expr nodes
    code: annotation string (excluding '@')
    nas_mode: the mode of NAS
    """
    module = ast.parse(code)
    assert type(module) is ast.Module, 'internal error #1'
    assert len(module.body) == 1, 'Annotation mutable_layers contains more than one expression'
    assert type(module.body[0]) is ast.Expr, 'Annotation is not expression'
    call = module.body[0].value
    nodes = []
    mutable_id = 'mutable_block_' + str(lineno)
    mutable_layer_cnt = 0
    for arg in call.args:
        fields = {'layer_choice': False,
                  'fixed_inputs': False,
                  'optional_inputs': False,
                  'optional_input_size': False,
                  'layer_output': False}
        for k, value in zip(arg.keys, arg.values):
            if k.id == 'layer_choice':
                assert not fields['layer_choice'], 'Duplicated field: layer_choice'
                assert type(value) is ast.List, 'Value of layer_choice should be a list'
                call_funcs_keys = []
                call_funcs_values = []
                call_kwargs_values = []
                for call in value.elts:
                    assert type(call) is ast.Call, 'Element in layer_choice should be function call'
                    call_name = astor.to_source(call).strip()
                    call_funcs_keys.append(ast.Str(s=call_name))
                    call_funcs_values.append(call.func)
                    assert not call.args, 'Number of args without keyword should be zero'
                    kw_args = []
                    kw_values = []
                    for kw in call.keywords:
                        kw_args.append(ast.Str(s=kw.arg))
                        kw_values.append(kw.value)
                    call_kwargs_values.append(ast.Dict(keys=kw_args, values=kw_values))
                call_funcs = ast.Dict(keys=call_funcs_keys, values=call_funcs_values)
                call_kwargs = ast.Dict(keys=call_funcs_keys, values=call_kwargs_values)
                fields['layer_choice'] = True
            elif k.id == 'fixed_inputs':
                assert not fields['fixed_inputs'], 'Duplicated field: fixed_inputs'
                assert type(value) is ast.List, 'Value of fixed_inputs should be a list'
                fixed_inputs = value
                fields['fixed_inputs'] = True
            elif k.id == 'optional_inputs':
                assert not fields['optional_inputs'], 'Duplicated field: optional_inputs'
                assert type(value) is ast.List, 'Value of optional_inputs should be a list'
                var_names = [ast.Str(s=astor.to_source(var).strip()) for var in value.elts]
                optional_inputs = ast.Dict(keys=var_names, values=value.elts)
                fields['optional_inputs'] = True
            elif k.id == 'optional_input_size':
                assert not fields['optional_input_size'], 'Duplicated field: optional_input_size'
                assert type(value) is ast.Num or type(value) is ast.List, \
                    'Value of optional_input_size should be a number or list'
                optional_input_size = value
                fields['optional_input_size'] = True
            elif k.id == 'layer_output':
                assert not fields['layer_output'], 'Duplicated field: layer_output'
                assert type(value) is ast.Name, 'Value of layer_output should be ast.Name type'
                layer_output = value
                fields['layer_output'] = True
            else:
                raise AssertionError('Unexpected field in mutable layer')
        # make call for this mutable layer
        assert fields['layer_choice'], 'layer_choice must exist'
        assert fields['layer_output'], 'layer_output must exist'
        mutable_layer_id = 'mutable_layer_' + str(mutable_layer_cnt)
        mutable_layer_cnt += 1
        target_call_attr = ast.Attribute(value=ast.Name(id='nni', ctx=ast.Load()), attr='mutable_layer', ctx=ast.Load())
        target_call_args = [ast.Str(s=mutable_id),
                            ast.Str(s=mutable_layer_id),
                            call_funcs,
                            call_kwargs]
        if fields['fixed_inputs']:
            target_call_args.append(fixed_inputs)
        else:
            target_call_args.append(ast.List(elts=[]))
        if fields['optional_inputs']:
            target_call_args.append(optional_inputs)
            assert fields['optional_input_size'], 'optional_input_size must exist when optional_inputs exists'
            target_call_args.append(optional_input_size)
        else:
            target_call_args.append(ast.Dict(keys=[], values=[]))
            target_call_args.append(ast.Num(n=0))
        target_call_args.append(ast.Str(s=nas_mode))
        if nas_mode in ['enas_mode', 'oneshot_mode', 'darts_mode']:
            target_call_args.append(ast.Name(id='tensorflow'))
        target_call = ast.Call(func=target_call_attr, args=target_call_args, keywords=[])
        node = ast.Assign(targets=[layer_output], value=target_call)
        nodes.append(node)
    return nodes