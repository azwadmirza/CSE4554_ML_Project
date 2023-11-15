def job_builder(args, meta):
    """
    Build a list of image processing jobs.
  
    Args:
        args: (object) argparse object.
        meta: metadata data structure.
    Returns:
    
    Raises:
    
    """
    # Overall job stack. List of list of jobs
    job_stack = []

    # Jobs/CPU (INT): divide the number of images by the number of requested CPU resources
    jobs_per_cpu = args.jobcount / args.cpu

    # Get the list of images
    # images = list(meta.keys())
    images = []
    for img in list(meta.keys()):
        # If a date range was requested, check whether the image is within range
        if args.dates:
            # Convert image datetime to unix time
            timestamp = dt_parser(meta[img]['timestamp'])
            time_delta = timestamp - datetime.datetime(1970, 1, 1)
            unix_time = (time_delta.days * 24 * 3600) + time_delta.seconds
            if unix_time < args.start_date or unix_time > args.end_date:
                continue
        if args.coprocess is not None:
            if meta[img]['imgtype'] != args.coprocess:
                images.append(img)
        else:
            images.append(img)

    print("Job list will include " + str(len(images)) + " images" + '\n', file=sys.stderr)

    # For each image
    for img in images:
        if (args.coprocess is not None) and ('coimg' in meta[img]):
            # Create an output file to store the co-image processing results and populate with metadata
            coimg = meta[meta[img]['coimg']]
            coout = file_writer("./{0}/{1}.txt".format(args.jobdir, meta[img]['coimg']))
            coout.write('\t'.join(map(str, ("META", "image", coimg['path'] + '/' + meta[img]['coimg']))) + '\n')
            # Valid metadata
            for m in list(args.valid_meta.keys()):
                coout.write('\t'.join(map(str, ("META", m, coimg[m]))) + '\n')

        # Create an output file to store the image processing results and populate with metadata
        outfile = file_writer("./{0}/{1}.txt".format(args.jobdir, img))
        outfile.write('\t'.join(map(str, ("META", "image", meta[img]['path'] + '/' + img))) + '\n')
        # Valid metadata
        for m in list(args.valid_meta.keys()):
            outfile.write('\t'.join(map(str, ("META", m, meta[img][m]))) + '\n')

        outfile.close()

    # Build the job stack
    # The first n - 1 CPUs will get INT jobs_per_cpu
    # The last CPU will get the remainder
    job = 0
    # For the first n - 1 CPU
    for c in range(1, args.cpu):
        # List of jobs for this CPU
        jobs = []

        # For each job/CPU
        for j in range(0, jobs_per_cpu):
            # Add job to list
            if args.coprocess is not None and ('coimg' in meta[images[job]]):
                job_str = "python {0} --image {1}/{2} --outdir {3} --result ./{4}/{5}.txt --coresult ./{6}/{7}.txt".format(
                    args.pipeline, meta[images[job]]['path'], images[job], args.outdir, args.jobdir, images[job],
                    args.jobdir, meta[images[job]]['coimg'])
                if args.writeimg:
                    job_str += ' --writeimg'
                if args.other_args:
                    job_str += ' ' + args.other_args
                jobs.append(job_str)
            else:
                job_str = "python {0} --image {1}/{2} --outdir {3} --result ./{4}/{5}.txt".format(args.pipeline,
                                                                                           meta[images[job]]['path'],
                                                                                           images[job], args.outdir,
                                                                                           args.jobdir, images[job])
                if args.writeimg:
                    job_str += ' --writeimg'
                if args.other_args:
                    job_str += ' ' + args.other_args
                jobs.append(job_str)

            # Increase the job counter by 1
            job += 1

        # Add the CPU job list to the job stack
        job_stack.append(jobs)

    # Add the remaining jobs to the last CPU
    jobs = []
    for j in range(job, len(images)):
        # Add job to list
        if args.coprocess is not None and ('coimg' in meta[images[j]]):
            job_str = "python {0} --image {1}/{2} --outdir {3} --result ./{4}/{5}.txt --coresult ./{6}/{7}.txt".format(
                args.pipeline, meta[images[j]]['path'], images[j], args.outdir, args.jobdir, images[j], args.jobdir,
                meta[images[j]]['coimg'])
            if args.writeimg:
                job_str += ' --writeimg'
            if args.other_args:
                job_str += ' ' + args.other_args
            jobs.append(job_str)
        else:
            job_str = "python {0} --image {1}/{2} --outdir {3} --result ./{4}/{5}.txt".format(args.pipeline,
                                                                                       meta[images[j]]['path'],
                                                                                       images[j], args.outdir,
                                                                                       args.jobdir, images[j])
            if args.writeimg:
                job_str += ' --writeimg'
            if args.other_args:
                job_str += ' ' + args.other_args
            jobs.append(job_str)
    # Add the CPU job list to the job stack
    job_stack.append(jobs)

    return job_stack