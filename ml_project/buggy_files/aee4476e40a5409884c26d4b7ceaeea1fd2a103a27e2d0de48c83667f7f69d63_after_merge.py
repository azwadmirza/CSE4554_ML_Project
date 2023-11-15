def resnet_train(
        project_id,
        output,
        region='us-central1',
        model='bolts',
        version='beta1',
        tf_version='1.12',
        train_csv='gs://bolts_image_dataset/bolt_images_train.csv',
        validation_csv='gs://bolts_image_dataset/bolt_images_validate.csv',
        labels='gs://bolts_image_dataset/labels.txt',
        depth=50,
        train_batch_size=1024,
        eval_batch_size=1024,
        steps_per_eval=250,
        train_steps=10000,
        num_train_images=218593,
        num_eval_images=54648,
        num_label_classes=10):
    output_dir = os.path.join(str(output), '{{workflow.name}}')
    preprocess_staging = os.path.join(output_dir, 'staging')
    preprocess_output = os.path.join(output_dir, 'preprocessed_output')
    train_output = os.path.join(output_dir, 'model')
    preprocess = resnet_preprocess_op(project_id, preprocess_output, preprocess_staging, train_csv,
                                      validation_csv, labels, train_batch_size, eval_batch_size).apply(gcp.use_gcp_secret())
    train = resnet_train_op(project_id, preprocess_output, train_output, region, depth, train_batch_size,
                            eval_batch_size, steps_per_eval, train_steps, num_train_images, num_eval_images,
                            num_label_classes, tf_version).apply(gcp.use_gcp_secret())
    train.after(preprocess)
    export_output = os.path.join(str(train.outputs['job_dir']), 'export')
    deploy = resnet_deploy_op(export_output, model, version, project_id, region,
                              tf_version).apply(gcp.use_gcp_secret())