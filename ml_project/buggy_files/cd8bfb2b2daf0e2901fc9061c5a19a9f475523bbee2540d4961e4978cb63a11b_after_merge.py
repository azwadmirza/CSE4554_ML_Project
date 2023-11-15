def get_parser():
    parser = configargparse.ArgumentParser(
        description='Train a new language model on one CPU or one GPU',
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter)
    # general configuration
    parser.add('--config', is_config_file=True, help='config file path')
    parser.add('--config2', is_config_file=True,
               help='second config file path that overwrites the settings in `--config`.')
    parser.add('--config3', is_config_file=True,
               help='third config file path that overwrites the settings in `--config` and `--config2`.')

    parser.add_argument('--ngpu', default=None, type=int,
                        help='Number of GPUs. If not given, use all visible devices')
    parser.add_argument('--backend', default='chainer', type=str,
                        choices=['chainer', 'pytorch'],
                        help='Backend library')
    parser.add_argument('--outdir', type=str, required=True,
                        help='Output directory')
    parser.add_argument('--debugmode', default=1, type=int,
                        help='Debugmode')
    parser.add_argument('--dict', type=str, required=True,
                        help='Dictionary')
    parser.add_argument('--seed', default=1, type=int,
                        help='Random seed')
    parser.add_argument('--resume', '-r', default='', nargs='?',
                        help='Resume the training from snapshot')
    parser.add_argument('--verbose', '-V', default=0, type=int,
                        help='Verbose option')
    parser.add_argument('--tensorboard-dir', default=None, type=str, nargs='?', help="Tensorboard log dir path")
    parser.add_argument('--report-interval-iters', default=100, type=int,
                        help="Report interval iterations")
    # task related
    parser.add_argument('--train-label', type=str, required=True,
                        help='Filename of train label data')
    parser.add_argument('--valid-label', type=str, required=True,
                        help='Filename of validation label data')
    parser.add_argument('--test-label', type=str,
                        help='Filename of test label data')
    # LSTMLM training configuration
    parser.add_argument('--opt', default='sgd', type=str,
                        choices=['sgd', 'adam'],
                        help='Optimizer')
    parser.add_argument('--sortagrad', default=0, type=int, nargs='?',
                        help="How many epochs to use sortagrad for. 0 = deactivated, -1 = all epochs")
    parser.add_argument('--batchsize', '-b', type=int, default=300,
                        help='Number of examples in each mini-batch')
    parser.add_argument('--epoch', '-e', type=int, default=20,
                        help='Number of sweeps over the dataset to train')
    parser.add_argument('--early-stop-criterion', default='validation/main/loss', type=str, nargs='?',
                        help="Value to monitor to trigger an early stopping of the training")
    parser.add_argument('--patience', default=3, type=int, nargs='?',
                        help="Number of epochs to wait without improvement before stopping the training")
    parser.add_argument('--gradclip', '-c', type=float, default=5,
                        help='Gradient norm threshold to clip')
    parser.add_argument('--type', type=str, default="lstm", nargs='?', choices=['lstm', 'gru'],
                        help="Which type of RNN to use")
    parser.add_argument('--layer', '-l', type=int, default=2,
                        help='Number of hidden layers')
    parser.add_argument('--unit', '-u', type=int, default=650,
                        help='Number of hidden units')
    parser.add_argument('--dropout-rate', type=float, default=0.5,
                        help='dropout probability')
    parser.add_argument('--maxlen', type=int, default=40,
                        help='Batch size is reduced if the input sequence > ML')
    parser.add_argument('--dump-hdf5-path', type=str, default=None,
                        help='Path to dump a preprocessed dataset as hdf5')
    return parser