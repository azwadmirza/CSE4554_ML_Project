def spec_to_image_mimebundle(spec, format, mode,
                             vega_version,
                             vegaembed_version,
                             vegalite_version=None,
                             driver_timeout=10):
    """Conver a vega/vega-lite specification to a PNG/SVG image

    Parameters
    ----------
    spec : dict
        a dictionary representing a vega-lite plot spec
    format : string {'png' | 'svg'}
        the file format to be saved.
    mode : string {'vega' | 'vega-lite'}
        The rendering mode.
    vega_version : string
        For html output, the version of vega.js to use
    vegalite_version : string
        For html output, the version of vegalite.js to use
    vegaembed_version : string
        For html output, the version of vegaembed.js to use
    driver_timeout : int (optional)
        the number of seconds to wait for page load before raising an
        error (default: 10)

    Returns
    -------
    output : dict
        a mime-bundle representing the image

    Note
    ----
    This requires the pillow, selenium, and chrome headless packages to be
    installed.
    """
    # TODO: allow package versions to be specified
    # TODO: detect & use local Jupyter caches of JS packages?
    if format not in ['png', 'svg']:
        raise NotImplementedError("format must be 'svg' and 'png'")
    if mode not in ['vega', 'vega-lite']:
        raise ValueError("mode must be 'vega' or 'vega-lite'")

    if mode == 'vega-lite' and vegalite_version is None:
        raise ValueError("must specify vega-lite version")

    if webdriver is None:
        raise ImportError("selenium package is required for saving chart as {0}".format(format))
    if ChromeOptions is None:
        raise ImportError("chromedriver is required for saving chart as {0}".format(format))

    html = HTML_TEMPLATE.format(vega_version=vega_version,
                                vegalite_version=vegalite_version,
                                vegaembed_version=vegaembed_version)

    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        if os.geteuid() == 0:
            chrome_options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.set_page_load_timeout(driver_timeout)

        try:
            fd, htmlfile = tempfile.mkstemp(suffix='.html', text=True)
            with open(htmlfile, 'w') as f:
                f.write(html)
            driver.get("file://" + htmlfile)
            online = driver.execute_script("return navigator.onLine")
            if not online:
                raise ValueError("Internet connection required for saving chart as {0}".format(format))
            render = driver.execute_async_script(EXTRACT_CODE[format],
                                                 spec, mode)
        finally:
            os.remove(htmlfile)
    finally:
        driver.close()

    if format == 'png':
        return {'image/png': base64.decodebytes(render.split(',', 1)[1].encode())}
    elif format == 'svg':
        return {'image/svg+xml': render}