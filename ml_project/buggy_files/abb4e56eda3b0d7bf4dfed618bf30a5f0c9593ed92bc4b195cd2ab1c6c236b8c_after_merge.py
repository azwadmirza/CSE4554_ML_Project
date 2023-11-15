def get_2d_uniform_color_shader():
    # return gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    uniform_2d_vertex_shader = '''
    in vec2 pos;
    uniform mat4 viewProjectionMatrix;
    uniform float x_offset;
    uniform float y_offset;

    void main()
    {
       gl_Position = viewProjectionMatrix * vec4(pos.x + x_offset, pos.y + y_offset, 0.0f, 1.0f);
    }
    '''

    uniform_2d_fragment_shader = '''
    uniform vec4 color;
    out vec4 gl_FragColor;
    void main()
    {
       gl_FragColor = color;
    }
    '''
    return gpu.types.GPUShader(uniform_2d_vertex_shader, uniform_2d_fragment_shader)