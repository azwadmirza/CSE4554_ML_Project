def remove_credentials(config: Dict[str, Any]) -> None:
    """
    Removes exchange keys from the configuration and specifies dry-run
    Used for backtesting / hyperopt / edge and utils.
    Modifies the input dict!
    """
    config['exchange']['key'] = ''
    config['exchange']['secret'] = ''
    config['exchange']['password'] = ''
    config['exchange']['uid'] = ''
    config['dry_run'] = True