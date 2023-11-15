def stats_viz_cat(
    data: Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]],
    plot_width: int,
    plot_height: int,
) -> Panel:
    """
    Render statistics panel for categorical data
    """
    # pylint: disable=line-too-long
    ov_content = ""
    lens_content = ""
    qs_content = ""
    ls_content = ""
    for key, value in data[0].items():
        value = _sci_notation_superscript(value)
        if "Distinct" in key and float(value) > 50:
            ov_content += _create_table_row(key, value, True)
        elif "Unique" in key and float(value.replace("%", "")) == 100:
            ov_content += _create_table_row(key, value, True)
        elif "Missing" in key and float(value.replace("%", "")) != 0:
            ov_content += _create_table_row(key, value, True)
        else:
            ov_content += _create_table_row(key, value)
    for key, value in data[1].items():
        lens_content += _create_table_row(key, value)
    for key, value in data[2].items():
        qs_content += _create_table_row(key, value)
    for key, value in data[3].items():
        ls_content += _create_table_row(key, value)

    ov_content = f"""
    <div style="grid-area: a;">
        <h3 style="text-align: center;">Overview</h3>
        <table style="width: 100%; table-layout: auto; font-size:11px;">
            <tbody>{ov_content}</tbody>
        </table>
    </div>
    """
    qs_content = f"""
    <div style="grid-area: b;">
        <h3 style="text-align: center;">Sample</h3>
        <table style="width: 100%; table-layout: auto; font-size:11px;">
            <tbody>{qs_content}</tbody>
        </table>
    </div>
    """
    ls_content = f"""
    <div style="grid-area: c;">
        <h3 style="text-align: center;">Letter</h3>
        <table style="width: 100%; table-layout: auto; font-size:11px;">
            <tbody>{ls_content}</tbody>
        </table>
    </div>
    """
    lens_content = f"""
    <div style="grid-area: d;">
        <h3 style="text-align: center;">Length</h3>
        <table style="width: 100%; table-layout: auto; font-size:11px;">
            <tbody>{lens_content}</tbody>
        </table>
    </div>
    """

    container = f"""<div style="display: grid;grid-template-columns: 1fr 1fr;grid-template-rows: 1fr 1fr;gap: 1px 1px;
                grid-template-areas:\'a b\' \'c d\';">
                {ov_content}{qs_content}{ls_content}{lens_content}</div>"""

    div = Div(
        text=container, width=plot_width, height=plot_height, style={"width": "100%"}
    )
    return Panel(child=div, title="stats")