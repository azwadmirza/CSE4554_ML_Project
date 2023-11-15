def get_2d_smooth_color_shader():
    # return gpu.shader.from_builtin('2D_SMOOTH_COLOR')
    smooth_2d_vertex_shader = '''
    in vec2 pos;
    layout(location=1) in vec4 color;

    uniform mat4 viewProjectionMatrix;
    uniform float x_offset;
    uniform float y_offset;

    out vec4 a_color;
   
    void main()
    {
        gl_Position = viewProjectionMatrix * vec4(pos.x + x_offset, pos.y + y_offset, 0.0f, 1.0f);
        a_color = color;
    }
    '''

    smooth_2d_fragment_shader = '''
    in vec4 a_color;

    void main()
    {
        gl_FragColor = a_color;
    }
    '''
    return gpu.types.GPUShader(smooth_2d_vertex_shader, smooth_2d_fragment_shader)    