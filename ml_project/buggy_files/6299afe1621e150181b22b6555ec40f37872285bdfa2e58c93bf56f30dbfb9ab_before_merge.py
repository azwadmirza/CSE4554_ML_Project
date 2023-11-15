def simple28_grid_xy(x, y, args):
    """ x and y are passed by default so you could add font content """

    geom, config = args
    back_color, grid_color, line_color = config.palette
    matrix = gpu.matrix.get_projection_matrix()

    bg_vertex_shader = '''
    in vec2 pos;
    uniform mat4 viewProjectionMatrix;
    uniform float x_offset;
    uniform float y_offset;

    void main()
    {
       gl_Position = viewProjectionMatrix * vec4(pos.x + x_offset, pos.y + y_offset, 0.0f, 1.0f);
    }
    '''

    bg_fragment_shader = '''
    uniform vec4 color;
    void main()
    {
       gl_FragColor = color;
    }
    '''

    shader = gpu.types.GPUShader(bg_vertex_shader, bg_fragment_shader)
    batch = batch_for_shader(shader, 'TRIS', {"pos": geom.background_coords}, indices=geom.background_indices)
    shader.bind()
    shader.uniform_float("color", back_color)
    shader.uniform_float("x_offset", x)
    shader.uniform_float("y_offset", y)
    shader.uniform_float("viewProjectionMatrix", matrix)
    batch.draw(shader)

    # draw grid and graph

    line_vertex_shader = '''
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

    line_fragment_shader = '''
    in vec4 a_color;

    void main()
    {
        gl_FragColor = a_color;
    }
    '''

    shader2 = gpu.types.GPUShader(line_vertex_shader, line_fragment_shader)
    batch2 = batch_for_shader(shader2, 'LINES', {"pos": geom.vertices, "color": geom.vertex_colors}, indices=geom.indices)
    shader2.bind()
    shader2.uniform_float("x_offset", x)
    shader2.uniform_float("y_offset", y)
    shader2.uniform_float("viewProjectionMatrix", matrix)
    batch2.draw(shader2)