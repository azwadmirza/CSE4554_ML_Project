def deploy_new_strategy(strategy_name, strategy_path: Path, subtemplate: str):
    """
    Deploy new strategy from template to strategy_path
    """
    indicators = render_template(templatefile=f"subtemplates/indicators_{subtemplate}.j2",)
    buy_trend = render_template(templatefile=f"subtemplates/buy_trend_{subtemplate}.j2",)
    sell_trend = render_template(templatefile=f"subtemplates/sell_trend_{subtemplate}.j2",)
    plot_config = render_template(templatefile=f"subtemplates/plot_config_{subtemplate}.j2",)

    strategy_text = render_template(templatefile='base_strategy.py.j2',
                                    arguments={"strategy": strategy_name,
                                               "indicators": indicators,
                                               "buy_trend": buy_trend,
                                               "sell_trend": sell_trend,
                                               "plot_config": plot_config,
                                               })

    logger.info(f"Writing strategy to `{strategy_path}`.")
    strategy_path.write_text(strategy_text)