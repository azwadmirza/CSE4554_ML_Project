def build_default_node(inp: bpy.types.NodeSocket):
    """Creates a new node to give a not connected input socket a value"""

    is_custom_socket = isinstance(inp, arm.logicnode.arm_sockets.ArmCustomSocket)

    if is_custom_socket:
        # ArmCustomSockets need to implement get_default_value()
        default_value = inp.get_default_value()
        if isinstance(default_value, str):
            default_value = '"{:s}"'.format(default_value.replace('"', '\\"') )
        inp_type = inp.arm_socket_type  # any custom socket's `type` is "VALUE". might as well have valuable type information for custom nodes as well.
    else:
        default_value = inp.default_value
        if isinstance(default_value, str):
            default_value = '"{:s}"'.format(default_value.replace('"', '\\"') )
        inp_type = inp.type

    # Don't write 'None' into the Haxe code
    if default_value is None:
        default_value = 'null'

    if inp_type == 'VECTOR':
        return f'new armory.logicnode.VectorNode(this, {default_value[0]}, {default_value[1]}, {default_value[2]})'
    elif inp_type == 'RGBA':
        return f'new armory.logicnode.ColorNode(this, {default_value[0]}, {default_value[1]}, {default_value[2]}, {default_value[3]})'
    elif inp_type == 'RGB':
        return f'new armory.logicnode.ColorNode(this, {default_value[0]}, {default_value[1]}, {default_value[2]})'
    elif inp_type == 'VALUE':
        return f'new armory.logicnode.FloatNode(this, {default_value})'
    elif inp_type == 'INT':
        return f'new armory.logicnode.IntegerNode(this, {default_value})'
    elif inp_type == 'BOOLEAN':
        return f'new armory.logicnode.BooleanNode(this, {str(default_value).lower()})'
    elif inp_type == 'STRING':
        return f'new armory.logicnode.StringNode(this, {default_value})'
    elif inp_type == 'NONE':
        return 'new armory.logicnode.NullNode(this)'
    elif inp_type == 'OBJECT':
        return f'new armory.logicnode.ObjectNode(this, {default_value})'
    elif is_custom_socket:
        return f'new armory.logicnode.DynamicNode(this, {default_value})'
    else:
        return 'new armory.logicnode.NullNode(this)'