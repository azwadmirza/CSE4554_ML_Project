def get_params():
    parser = argparse.ArgumentParser()
    # Data path
    parser.add_argument('--datastore', type=str, dest='datastore', help="Datastore path")
    parser.add_argument('--train-datapath', type=str, dest='train_datapath')
    parser.add_argument('--validation-datapath', type=str, dest='validation_datapath')
    parser.add_argument('--surprise-reader', type=str, dest='surprise_reader')
    parser.add_argument('--usercol', type=str, dest='usercol', default='userID')
    parser.add_argument('--itemcol', type=str, dest='itemcol', default='itemID')
    # Metrics
    parser.add_argument('--rating-metrics', type=str, nargs='*', dest='rating_metrics', default=[])
    parser.add_argument('--ranking-metrics', type=str, nargs='*', dest='ranking_metrics', default=[])
    parser.add_argument('--k', type=int, dest='k', default=None)
    parser.add_argument('--remove-seen', dest='remove_seen', action='store_false')
    # Training parameters
    parser.add_argument('--random-state', type=int, dest='random_state', default=0)
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.add_argument('--epochs', type=int, dest='n_epochs', default=30)
    parser.add_argument('--biased', dest='biased', action='store_true')
    parser.add_argument('--primary-metric', dest='primary_metric', default='rmse')
    # Hyperparameters to be tuned
    parser.add_argument('--n_factors', type=int, dest='n_factors', default=100)
    parser.add_argument('--init_mean', type=float, dest='init_mean', default=0.0)
    parser.add_argument('--init_std_dev', type=float, dest='init_std_dev', default=0.1)
    parser.add_argument('--lr_all', type=float, dest='lr_all', default=0.005)
    parser.add_argument('--reg_all', type=float, dest='reg_all', default=0.02)
    parser.add_argument('--lr_bu', type=float, dest='lr_bu', default=None)
    parser.add_argument('--lr_bi', type=float, dest='lr_bi', default=None)
    parser.add_argument('--lr_pu', type=float, dest='lr_pu', default=None)
    parser.add_argument('--lr_qi', type=float, dest='lr_qi', default=None)
    parser.add_argument('--reg_bu', type=float, dest='reg_bu', default=None)
    parser.add_argument('--reg_bi', type=float, dest='reg_bi', default=None)
    parser.add_argument('--reg_pu', type=float, dest='reg_pu', default=None)
    parser.add_argument('--reg_qi', type=float, dest='reg_qi', default=None)

    args = parser.parse_args()
    return args