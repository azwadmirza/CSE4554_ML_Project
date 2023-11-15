def main():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("run", choices=["train", "infer", "export"],
                      help="Run type.")
  parser.add_argument("--config", required=True, nargs="+",
                      help="List of configuration files.")
  parser.add_argument("--model", default="",
                      help="Model configuration file.")
  parser.add_argument("--run_dir", default="",
                      help="If set, model_dir will be created relative to this location.")
  parser.add_argument("--data_dir", default="",
                      help="If set, data files are expected to be relative to this location.")
  parser.add_argument("--features_file", default=[], nargs="+",
                      help="Run inference on this file.")
  parser.add_argument("--predictions_file", default="",
                      help=("File used to save predictions. If not set, predictions are printed "
                            "on the standard output."))
  parser.add_argument("--checkpoint_path", default=None,
                      help="Checkpoint to use for inference or export (latest by default).")
  parser.add_argument("--chief_host", default="",
                      help="hostname:port of the chief worker (for distributed training).")
  parser.add_argument("--worker_hosts", default="",
                      help=("Comma-separated list of hostname:port of workers "
                            "(for distributed training)."))
  parser.add_argument("--ps_hosts", default="",
                      help=("Comma-separated list of hostname:port of parameter servers "
                            "(for distributed training)."))
  parser.add_argument("--task_type", default="chief",
                      choices=["chief", "worker", "ps", "evaluator"],
                      help="Type of the task to run (for distributed training).")
  parser.add_argument("--task_index", type=int, default=0,
                      help="ID of the task (for distributed training).")
  parser.add_argument("--log_level", default="INFO",
                      choices=["DEBUG", "ERROR", "FATAL", "INFO", "WARN"],
                      help="Logs verbosity.")
  parser.add_argument("--gpu_allow_growth", type=bool, default=False,
                      help="Allocate GPU memory dynamically.")
  args = parser.parse_args()

  tf.logging.set_verbosity(getattr(tf.logging, args.log_level))

  # Setup cluster if defined.
  if args.chief_host:
    os.environ["TF_CONFIG"] = json.dumps({
        "cluster": {
            "chief": args.chief_host,
            "worker": args.worker_hosts.split(","),
            "ps": args.ps_hosts.split(",")
        },
        "task": {
            "type": args.task_type,
            "index": args.task_index
        }
    })

  # Load and merge run configurations.
  config = load_config(args.config)

  if args.run_dir:
    config["model_dir"] = _prefix_path(args.run_dir, config["model_dir"])
  if not os.path.isdir(config["model_dir"]):
    tf.logging.info("Creating model directory %s", config["model_dir"])
    os.makedirs(config["model_dir"])

  session_config = tf.ConfigProto()
  session_config.gpu_options.allow_growth = args.gpu_allow_growth

  run_config = tf.estimator.RunConfig(
      model_dir=config["model_dir"],
      session_config=session_config)

  if "train" in config:
    if "save_summary_steps" in config["train"]:
      run_config = run_config.replace(
          save_summary_steps=config["train"]["save_summary_steps"],
          log_step_count_steps=config["train"]["save_summary_steps"])
    if "save_checkpoints_steps" in config["train"]:
      run_config = run_config.replace(
          save_checkpoints_secs=None,
          save_checkpoints_steps=config["train"]["save_checkpoints_steps"])
    if "keep_checkpoint_max" in config["train"]:
      run_config = run_config.replace(
          keep_checkpoint_max=config["train"]["keep_checkpoint_max"])

  model = load_model(config["model_dir"], model_file=args.model)

  estimator = tf.estimator.Estimator(
      model,
      config=run_config,
      params=config["params"])

  if args.run == "train":
    if args.data_dir:
      config["data"] = _prefix_path(args.data_dir, config["data"])
    train(estimator, model, config)
  elif args.run == "infer":
    if not args.features_file:
      parser.error("--features_file is required for inference.")
    elif len(args.features_file) == 1:
      args.features_file = args.features_file[0]
    infer(
        args.features_file,
        estimator,
        model,
        config,
        checkpoint_path=args.checkpoint_path,
        predictions_file=args.predictions_file)
  elif args.run == "export":
    export(estimator, model, config, checkpoint_path=args.checkpoint_path)