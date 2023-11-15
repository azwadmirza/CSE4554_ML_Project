def deploy_new_hyperopt(hyperopt_name: str, hyperopt_path: Path, subtemplate: str) -> None:
    """
    Deploys a new hyperopt template to hyperopt_path
    """
    buy_guards = render_template(
        templatefile=f"subtemplates/hyperopt_buy_guards_{subtemplate}.j2",)
    sell_guards = render_template(
        templatefile=f"subtemplates/hyperopt_sell_guards_{subtemplate}.j2",)
    buy_space = render_template(
        templatefile=f"subtemplates/hyperopt_buy_space_{subtemplate}.j2",)
    sell_space = render_template(
        templatefile=f"subtemplates/hyperopt_sell_space_{subtemplate}.j2",)

    strategy_text = render_template(templatefile='base_hyperopt.py.j2',
                                    arguments={"hyperopt": hyperopt_name,
                                               "buy_guards": buy_guards,
                                               "sell_guards": sell_guards,
                                               "buy_space": buy_space,
                                               "sell_space": sell_space,
                                               })

    logger.info(f"Writing hyperopt to `{hyperopt_path}`.")
    hyperopt_path.write_text(strategy_text)