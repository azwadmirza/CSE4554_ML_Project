def _install_css_and_js_files():
    with OperateInDirectory('../web_interface/static'):
        os.makedirs('web_css', exist_ok=True)
        os.makedirs('web_js', exist_ok=True)

        wget_static_web_content('https://github.com/vakata/jstree/zipball/3.3.9', '.', ['unzip 3.3.9', 'rm 3.3.9', 'rm -rf ./web_js/jstree/vakata*', 'mv vakata* web_js/jstree'], 'jstree')
        wget_static_web_content('https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js', '.', [], 'angularJS')
        wget_static_web_content('https://github.com/chartjs/Chart.js/releases/download/v2.3.0/Chart.js', '.', [], 'charts.js')

        _build_highlight_js()

        for css_url in [
                'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.8.0/css/bootstrap-datepicker.standalone.css'
        ]:
            wget_static_web_content(css_url, 'web_css', [])

        for js_url in [
                'https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.1/jquery.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js',
                'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.8.0/js/bootstrap-datepicker.js',
                'https://raw.githubusercontent.com/moment/moment/develop/moment.js'
        ]:
            wget_static_web_content(js_url, 'web_js', [])

        if not Path('web_css/fontawesome').exists():
            wget_static_web_content(
                'https://use.fontawesome.com/releases/v5.13.0/fontawesome-free-5.13.0-web.zip',
                '.',
                [
                    'unzip fontawesome-free-5.13.0-web.zip',
                    'rm fontawesome-free-5.13.0-web.zip',
                    'mv fontawesome-free-5.13.0-web web_css/fontawesome'
                ]
            )

        if not Path('bootstrap3-editable').exists():
            wget_static_web_content(
                'https://vitalets.github.io/x-editable/assets/zip/bootstrap3-editable-1.5.1.zip',
                '.',
                ['unzip -o bootstrap3-editable-1.5.1.zip',
                 'rm bootstrap3-editable-1.5.1.zip CHANGELOG.txt LICENSE-MIT README.md',
                 'rm -rf inputs-ext'],
                'x-editable')