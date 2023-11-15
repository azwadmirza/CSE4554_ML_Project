def populate_state( request_context, inputs, incoming, state, errors={}, prefix='', context=None, check=True ):
    """
    Populates nested state dict from incoming parameter values.
    >>> from xml.etree.ElementTree import XML
    >>> from galaxy.util.bunch import Bunch
    >>> from galaxy.util.odict import odict
    >>> from galaxy.tools.parameters.basic import TextToolParameter, BooleanToolParameter
    >>> from galaxy.tools.parameters.grouping import Repeat
    >>> trans = Bunch( workflow_building_mode=False )
    >>> a = TextToolParameter( None, XML( '<param name="a"/>' ) )
    >>> b = Repeat()
    >>> b.min = 0
    >>> b.max = 1
    >>> c = TextToolParameter( None, XML( '<param name="c"/>' ) )
    >>> d = Repeat()
    >>> d.min = 0
    >>> d.max = 1
    >>> e = TextToolParameter( None, XML( '<param name="e"/>' ) )
    >>> f = Conditional()
    >>> g = BooleanToolParameter( None, XML( '<param name="g"/>' ) )
    >>> h = TextToolParameter( None, XML( '<param name="h"/>' ) )
    >>> i = TextToolParameter( None, XML( '<param name="i"/>' ) )
    >>> b.name = 'b'
    >>> b.inputs = odict([ ('c', c), ('d', d) ])
    >>> d.name = 'd'
    >>> d.inputs = odict([ ('e', e), ('f', f) ])
    >>> f.test_param = g
    >>> f.name = 'f'
    >>> f.cases = [ Bunch( value='true', inputs= { 'h': h } ), Bunch( value='false', inputs= { 'i': i } ) ]
    >>> inputs = odict([('a',a),('b',b)])
    >>> flat = odict([ ('a', 1 ), ( 'b_0|c', 2 ), ( 'b_0|d_0|e', 3 ), ( 'b_0|d_0|f|h', 4 ), ( 'b_0|d_0|f|g', True ) ])
    >>> state = odict()
    >>> populate_state( trans, inputs, flat, state, check=False )
    >>> print state[ 'a' ]
    1
    >>> print state[ 'b' ][ 0 ][ 'c' ]
    2
    >>> print state[ 'b' ][ 0 ][ 'd' ][ 0 ][ 'e' ]
    3
    >>> print state[ 'b' ][ 0 ][ 'd' ][ 0 ][ 'f' ][ 'h' ]
    4
    """
    context = ExpressionContext( state, context )
    for input in inputs.values():
        state[ input.name ] = input.get_initial_value( request_context, context )
        key = prefix + input.name
        group_state = state[ input.name ]
        group_prefix = '%s|' % ( key )
        if input.type == 'repeat':
            rep_index = 0
            del group_state[:]
            while True:
                rep_prefix = '%s_%d' % ( key, rep_index )
                if not any( incoming_key.startswith( rep_prefix ) for incoming_key in incoming.keys() ) and rep_index >= input.min:
                    break
                if rep_index < input.max:
                    new_state = { '__index__' : rep_index }
                    group_state.append( new_state )
                    populate_state( request_context, input.inputs, incoming, new_state, errors, prefix=rep_prefix + '|', context=context )
                rep_index += 1
        elif input.type == 'conditional':
            if input.value_ref and not input.value_ref_in_group:
                test_param_key = prefix + input.test_param.name
            else:
                test_param_key = group_prefix + input.test_param.name
            test_param_value = incoming.get( test_param_key, group_state.get( input.test_param.name ) )
            value, error = check_param( request_context, input.test_param, test_param_value, context ) if check else [ test_param_value, None ]
            if error:
                errors[ test_param_key ] = error
            else:
                try:
                    current_case = input.get_current_case( value )
                    group_state = state[ input.name ] = {}
                    populate_state( request_context, input.cases[ current_case ].inputs, incoming, group_state, errors, prefix=group_prefix, context=context )
                    group_state[ '__current_case__' ] = current_case
                except Exception:
                    errors[ test_param_key ] = 'The selected case is unavailable/invalid.'
                    pass
            group_state[ input.test_param.name ] = value
        elif input.type == 'section':
            populate_state( request_context, input.inputs, incoming, group_state, errors, prefix=group_prefix, context=context )
        elif input.type == 'upload_dataset':
            d_type = input.get_datatype( request_context, context=context )
            writable_files = d_type.writable_files
            while len( group_state ) > len( writable_files ):
                del group_state[ -1 ]
            while len( writable_files ) > len( group_state ):
                new_state = { '__index__' : len( group_state ) }
                for upload_item in input.inputs.values():
                    new_state[ upload_item.name ] = upload_item.get_initial_value( request_context, context )
                group_state.append( new_state )
            for i, rep_state in enumerate( group_state ):
                rep_index = rep_state[ '__index__' ]
                rep_prefix = '%s_%d|' % ( key, rep_index )
                populate_state( request_context, input.inputs, incoming, rep_state, errors, prefix=rep_prefix, context=context )
        else:
            param_value = _get_incoming_value( incoming, key, state.get( input.name ) )
            value, error = check_param( request_context, input, param_value, context ) if check else [ param_value, None ]
            if error:
                errors[ key ] = error
            state[ input.name ] = value