def generate_file_rst(fname, target_dir, src_dir, root_dir, plot_gallery):
    """ Generate the rst file for a given example.
    """
    base_image_name = os.path.splitext(fname)[0]
    image_fname = '%s_%%03d.png' % base_image_name

    this_template = rst_template
    last_dir = os.path.split(src_dir)[-1]
    # to avoid leading . in file names, and wrong names in links
    if last_dir == '.' or last_dir == 'examples':
        last_dir = ''
    else:
        last_dir += '_'
    short_fname = last_dir + fname
    src_file = os.path.join(src_dir, fname)
    example_file = os.path.join(target_dir, fname)
    shutil.copyfile(src_file, example_file)

    # The following is a list containing all the figure names
    figure_list = []

    image_dir = os.path.join(target_dir, 'images')
    thumb_dir = os.path.join(image_dir, 'thumb')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)
    image_path = os.path.join(image_dir, image_fname)
    stdout_path = os.path.join(image_dir,
                               'stdout_%s.txt' % base_image_name)
    time_path = os.path.join(image_dir,
                             'time_%s.txt' % base_image_name)
    thumb_file = os.path.join(thumb_dir, fname[:-3] + '.png')
    time_elapsed = 0
    time_m = 0
    time_s = 0
    if plot_gallery and fname.startswith('plot'):
        # generate the plot as png image if file name
        # starts with plot and if it is more recent than an
        # existing image.
        first_image_file = image_path % 1
        if os.path.exists(stdout_path):
            stdout = open(stdout_path).read()
        else:
            stdout = ''
        if os.path.exists(time_path):
            time_elapsed = float(open(time_path).read())

        if not os.path.exists(first_image_file) or \
           os.stat(first_image_file).st_mtime <= os.stat(src_file).st_mtime:
            # We need to execute the code
            print('plotting %s' % fname)
            t0 = time()
            import matplotlib.pyplot as plt
            plt.close('all')
            cwd = os.getcwd()
            try:
                # First CD in the original example dir, so that any file
                # created by the example get created in this directory
                orig_stdout = sys.stdout
                os.chdir(os.path.dirname(src_file))
                my_buffer = StringIO()
                my_stdout = Tee(sys.stdout, my_buffer)
                sys.stdout = my_stdout
                my_globals = {'pl': plt}
                execfile(os.path.basename(src_file), my_globals)
                time_elapsed = time() - t0
                sys.stdout = orig_stdout
                my_stdout = my_buffer.getvalue()

                if '__doc__' in my_globals:
                    # The __doc__ is often printed in the example, we
                    # don't with to echo it
                    my_stdout = my_stdout.replace(
                        my_globals['__doc__'],
                        '')
                my_stdout = my_stdout.strip()
                if my_stdout:
                    stdout = '**Script output**::\n\n  %s\n\n' % (
                        '\n  '.join(my_stdout.split('\n')))
                open(stdout_path, 'w').write(stdout)
                open(time_path, 'w').write('%f' % time_elapsed)
                os.chdir(cwd)

                # In order to save every figure we have two solutions :
                # * iterate from 1 to infinity and call plt.fignum_exists(n)
                #   (this requires the figures to be numbered
                #    incrementally: 1, 2, 3 and not 1, 2, 5)
                # * iterate over [fig_mngr.num for fig_mngr in
                #   matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
                for fig_num in (fig_mngr.num for fig_mngr in
                    matplotlib._pylab_helpers.Gcf.get_all_fig_managers()):
                    # Set the fig_num figure as the current figure as we can't
                    # save a figure that's not the current figure.
                    plt.figure(fig_num)
                    plt.savefig(image_path % fig_num)
                    figure_list.append(image_fname % fig_num)
            except:
                print(80 * '_')
                print('%s is not compiling:' % fname)
                traceback.print_exc()
                print(80 * '_')
            finally:
                os.chdir(cwd)
                sys.stdout = orig_stdout

            print(" - time elapsed : %.2g sec" % time_elapsed)
        else:
            figure_list = [f[len(image_dir):]
                           for f in glob.glob(image_path.replace("%03d",
                                                '[0-9][0-9][0-9]'))]
        figure_list.sort()

        # generate thumb file
        this_template = plot_rst_template
        car_thumb_path =  os.path.join(os.path.split(root_dir)[0], '_build/html/stable/_images/')
        # Note: normaly, make_thumbnail is used to write to the path contained in `thumb_file`
        # which is within `auto_examples/../images/thumbs` depending on the example.
        # Because the carousel has different dimensions than those of the examples gallery,
        # I did not simply reuse them all as some contained whitespace due to their default gallery
        # thumbnail size. Below, for a few cases, seperate thumbnails are created (the originals can't
        # just be overwritten with the carousel dimensions as it messes up the examples gallery layout).
        # The special carousel thumbnails are written directly to _build/html/stable/_images/,
        # as for some reason unknown to me, Sphinx refuses to copy my 'extra' thumbnails from the
        # auto examples gallery to the _build folder. This works fine as is, but it would be cleaner to
        # have it happen with the rest. Ideally the should be written to 'thumb_file' as well, and then
        # copied to the _images folder during the `Copying Downloadable Files` step like the rest.
        if not os.path.exists(car_thumb_path):
            os.makedirs(car_thumb_path)
        if os.path.exists(first_image_file):
            # We generate extra special thumbnails for the carousel
            carousel_tfile = os.path.join(car_thumb_path, fname[:-3] + '_carousel.png')
            first_img = image_fname % 1
            if first_img in carousel_thumbs:
                make_thumbnail((image_path % carousel_thumbs[first_img][0]),
                               carousel_tfile, carousel_thumbs[first_img][1], 190)
            make_thumbnail(first_image_file, thumb_file, 400, 280)

    if not os.path.exists(thumb_file):
        # create something to replace the thumbnail
        make_thumbnail('images/no_image.png', thumb_file, 200, 140)

    docstring, short_desc, end_row = extract_docstring(example_file)

    # Depending on whether we have one or more figures, we're using a
    # horizontal list or a single rst call to 'image'.
    if len(figure_list) == 1:
        figure_name = figure_list[0]
        image_list = SINGLE_IMAGE % figure_name.lstrip('/')
    else:
        image_list = HLIST_HEADER
        for figure_name in figure_list:
            image_list += HLIST_IMAGE_TEMPLATE % figure_name.lstrip('/')

    time_m, time_s = divmod(time_elapsed, 60)
    f = open(os.path.join(target_dir, fname[:-2] + 'rst'), 'w')
    f.write(this_template % locals())
    f.flush()

    # save variables so we can later add links to the documentation
    example_code_obj = identify_names(open(example_file).read())
    if example_code_obj:
        codeobj_fname = example_file[:-3] + '_codeobj.pickle'
        with open(codeobj_fname, 'wb') as fid:
            pickle.dump(example_code_obj, fid, pickle.HIGHEST_PROTOCOL)