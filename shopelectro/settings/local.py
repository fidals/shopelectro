PIPELINE = {
    'CSS_COMPRESSOR': None,
    'LESS_BINARY': 'C:\\htdocs\\shopelectro\\node_modules\\.bin\\lessc.cmd',
    'LESS_ARGUMENTS': '--rootpath=../',
    'STYLESHEETS': {
        'styles': {
            'source_filenames': (
                'front/less/styles.less',
            ),
            'output_filename': 'build/css/styles.css',
        },
        'main': {
            'source_filenames': (
                'front/less/pages/main.less',
            ),
            'output_filename': 'build/css/main.css',
        },
    },
    'JS_COMPRESSOR': None,
    'BABEL_BINARY': 'C:\\htdocs\\shopelectro\\node_modules\\.bin\\babel.cmd',
    'BABEL_ARGUMENTS': '--presets es2015',
    'JAVASCRIPT': {
        'vendors': {
            'source_filenames': (
                'front/js/vendors/jquery-2.2.3.min.js',
                'front/js/vendors/jquery-ui-1.10.3.custom.min.js',
                'front/js/vendors/bootstrap.min.js',
                'front/js/vendors/jquery.mask.min.js',
                'front/js/vendors/jscrollpane.js',
            ),
            'output_filename': 'build/js/vendors.js',
        },
        'main': {
            'source_filenames': (
                'front/js/server.es6',
                'front/js/main.es6',
            ),
            'output_filename': 'build/js/main.js',
        }
    },
    'COMPILERS': (
        'pipeline.compilers.less.LessCompiler',
        'pipeline.compilers.es6.ES6Compiler',
    )
}