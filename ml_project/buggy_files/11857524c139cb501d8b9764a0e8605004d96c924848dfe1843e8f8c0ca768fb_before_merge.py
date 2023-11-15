def options():
    """Parse command line options.
    
    Args:
    
    Returns:
        argparse object.
    Raises:
        IOError: if dir does not exist.
        IOError: if pipeline does not exist.
        IOError: if the metadata file SnapshotInfo.csv does not exist in dir when flat is False.
        ValueError: if adaptor is not phenofront or dbimportexport.
        ValueError: if a metadata field is not supported.
    """
    # Job start time
    start_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    print("Starting run " + start_time + '\n', file=sys.stderr)

    # These are metadata types that PlantCV deals with.
    # Values are default values in the event the metadata is missing
    valid_meta = {
        # Camera settings
        'camera': 'none',
        'imgtype': 'none',
        'zoom': 'none',
        'exposure': 'none',
        'gain': 'none',
        'frame': 'none',
        'lifter': 'none',
        # Date-Time
        'timestamp': 'none',
        # Sample attributes
        'id': 'none',
        'plantbarcode': 'none',
        'treatment': 'none',
        'cartag': 'none',
        # Experiment attributes
        'measurementlabel': 'none',
        # Other
        'other': 'none'
    }
    parser = argparse.ArgumentParser(description='Parallel imaging processing with PlantCV.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--dir", help='Input directory containing images or snapshots.', required=True)
    parser.add_argument("-a", "--adaptor",
                        help='Image metadata reader adaptor. PhenoFront metadata is stored in a CSV file and the '
                             'image file name. For the filename option, all metadata is stored in the image file '
                             'name. Current adaptors: phenofront, image', default="phenofront")
    parser.add_argument("-p", "--pipeline", help='Pipeline script file.', required=True)
    parser.add_argument("-s", "--db", help='SQLite database file name.', required=True)
    parser.add_argument("-i", "--outdir", help='Output directory for images. Not required by all pipelines.',
                        default=".")
    parser.add_argument("-T", "--cpu", help='Number of CPU to use.', default=1, type=int)
    parser.add_argument("-c", "--create",
                        help='Create output database (SQLite). Default behaviour adds to existing database. '
                             'Warning: activating this option will delete an existing database!',
                        default=False, action="store_true")
    parser.add_argument("-m", "--roi", help='ROI/mask image. Required by some pipelines (vis_tv, flu_tv).',
                        required=False)
    parser.add_argument("-D", "--dates",
                        help='Date range. Format: YYYY-MM-DD-hh-mm-ss_YYYY-MM-DD-hh-mm-ss. If the second date '
                             'is excluded then the current date is assumed.',
                        required=False)
    parser.add_argument("-t", "--type", help='Image format type (extension).', default="png")
    parser.add_argument("-l", "--deliminator", help='Image file name metadata deliminator character.', default='_')
    parser.add_argument("-f", "--meta",
                        help='Image file name metadata format. List valid metadata fields separated by the '
                             'deliminator (-l/--deliminator). Valid metadata fields are: ' +
                             ', '.join(map(str, list(valid_meta.keys()))), default='imgtype_camera_frame_zoom_id')
    parser.add_argument("-M", "--match",
                        help='Restrict analysis to images with metadata matching input criteria. Input a '
                             'metadata:value comma-separated list. This is an exact match search. '
                             'E.g. imgtype:VIS,camera:SV,zoom:z500',
                        required=False)
    parser.add_argument("-C", "--coprocess",
                        help='Coprocess the specified imgtype with the imgtype specified in --match '
                             '(e.g. coprocess NIR images with VIS).',
                        default=None)
    parser.add_argument("-w", "--writeimg", help='Include analysis images in output.', default=False,
                        action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.dir):
        raise IOError("Directory does not exist: {0}".format(args.dir))
    if not os.path.exists(args.pipeline):
        raise IOError("File does not exist: {0}".format(args.pipeline))
    if args.adaptor is 'phenofront':
        if not os.path.exists(args.dir + '/SnapshotInfo.csv'):
            raise IOError(
                'The snapshot metadata file SnapshotInfo.csv does not exist in {0}. '
                'Perhaps you meant to use a different adaptor?'.format(
                    args.dir))
    if not os.path.exists(args.outdir):
        raise IOError("Directory does not exist: {0}".format(args.outdir))

    args.jobdir = start_time
    try:
        os.makedirs(args.jobdir)
    except IOError as e:
        raise IOError("{0}: {1}".format(e.strerror, args.jobdir))

    if args.adaptor != 'phenofront' and args.adaptor != 'filename':
        raise ValueError("Adaptor must be either phenofront or filename")

    if args.dates:
        dates = args.dates.split('_')
        if len(dates) == 1:
            # End is current time
            dates.append(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
        start = map(int, dates[0].split('-'))
        end = map(int, dates[1].split('-'))
        # Convert start and end dates to Unix time
        start_td = datetime.datetime(*start) - datetime.datetime(1970, 1, 1)
        end_td = datetime.datetime(*end) - datetime.datetime(1970, 1, 1)
        args.start_date = (start_td.days * 24 * 3600) + start_td.seconds
        args.end_date = (end_td.days * 24 * 3600) + end_td.seconds
    else:
        end = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        end_list = map(int, end.split('-'))
        end_td = datetime.datetime(*end_list) - datetime.datetime(1970, 1, 1)
        args.start_date = 1
        args.end_date = (end_td.days * 24 * 3600) + end_td.seconds

    args.valid_meta = valid_meta
    args.start_time = start_time

    # Image filename metadata structure
    fields = args.meta.split(args.deliminator)
    structure = {}
    for i, field in enumerate(fields):
        structure[field] = i
    args.fields = structure

    # Are the user-defined metadata valid?
    for field in args.fields:
        if field not in args.valid_meta:
            raise ValueError("The field {0} is not a currently supported metadata type.".format(field))

    # Metadata restrictions
    args.imgtype = {}
    if args.match is not None:
        pairs = args.match.split(',')
        for pair in pairs:
            key, value = pair.split(':')
            args.imgtype[key] = value
    else:
        args.imgtype['None'] = 'None'

    if (args.coprocess is not None) and ('imgtype' not in args.imgtype):
        raise ValueError("When the coprocess imgtype is defined, imgtype must be included in match.")

    return args