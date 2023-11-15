def generate_take_cython_file(path='generated.pyx'):
    with open(path, 'w') as f:
        print >> f, header

        print >> f, generate_ensure_dtypes()

        for template in templates_1d:
            print >> f, generate_from_template(template)

        for template in templates_2d:
            print >> f, generate_from_template(template, ndim=2)

        # for template in templates_1d_datetime:
        #     print >> f, generate_from_template_datetime(template)

        # for template in templates_2d_datetime:
        #     print >> f, generate_from_template_datetime(template, ndim=2)

        for template in nobool_1d_templates:
            print >> f, generate_from_template(template, exclude=['bool'])