// ================================================================
// IMPORTS
// ================================================================
import gulp from 'gulp';
import del from 'del';
import lessGlob from 'less-plugin-glob';
import sequence from 'run-sequence';
import babelPreset from 'babel-preset-es2015';

const $ = require('gulp-load-plugins')();
const spawnSync = require('child_process').spawnSync;

// ================================================================
// Utils
// ================================================================

/**
 * Get src paths from given appName.
 * Usage:
 *   appPath = getAppSrcPath('pages')
 *   const path = {
 *     src: {
 *       styles: [
 *         'front/less/styles.less',
 *         'front/less/pages.less',
 *         ...appPath.styles,
 *       ],
 * @param {string} appName
 * @returns {Object} - app's source file paths
 *   (ex. {styles: ['~/app_name/front/styles/style.less'], ...})
 */
function getAppSrcPaths(appName) {
  const processData = spawnSync('python3', ['manage.py', 'get_app_path_for_gulp', appName]);
  const err = processData.stderr.toString().trim();
  if (err) throw Error(err);

  const appPath = processData.stdout.toString().trim();
  return require(appPath + '/front/paths.js');
}

// ================================================================
// CONSTS
// ================================================================
const env = {
  development: true,
  production: false,
};

const buildDir = 'front/build';
const genericAdminPaths = getAppSrcPaths('generic_admin');

const path = {
  src: {
    styles: {
      admin: [
        ...genericAdminPaths.css,
      ],
      main: [
        'front/less/styles.less',
        'front/less/pages.less',
      ],
    },

    js: {
      vendors: [
        'front/js/vendors/jquery-2.2.3.min.js',
        'front/js/vendors/bootstrap.min.js',
        'front/js/vendors/js.cookie.js',
        'front/js/vendors/jscrollpane.js',
        'front/js/vendors/jquery.mask.min.js',
        'front/js/vendors/jquery.bootstrap-touchspin.min.js',
        'front/js/vendors/autocomplete.min.js',
        'front/js/vendors/babel.polyfill.min.js',
      ],

      main: [
        'front/js/shared/*.es6',
        'front/js/components/orderCall.es6',
        'front/js/components/headerCart.es6',
        'front/js/components/main.es6',
        'front/js/components/autocomplete.es6',
      ],

      pages: [
        'front/js/vendors/bootstrap-select.js',
        'front/js/vendors/jquery.fancybox.min.js',
        'front/js/shared/helpers.es6',
        'front/js/components/category.es6',
        'front/js/components/product.es6',
        'front/js/components/order.es6',
        'front/js/components/accordion.es6',
        'front/js/components/staticPages.es6',
      ],

      adminVendors: [
        ...genericAdminPaths.vendors,
      ],

      admin: [
        ...genericAdminPaths.admin,
        'front/js/components/admin.es6',
      ],
    },

    images: [
      'front/images/**/*',
      genericAdminPaths.img,
    ],

    fonts: 'front/fonts/**/*',
  },

  build: {
    styles: `${buildDir}/css/`,
    js: `${buildDir}/js/`,
    images: `${buildDir}/images/`,
    fonts: `${buildDir}/fonts/`,
  },

  watch: {
    styles: [
      'front/less/**/*',
      genericAdminPaths.watch.css,
    ],
    js: [
      'front/js/**/*',
      genericAdminPaths.watch.js,
    ],
    images: 'src/images/**/*',
    fonts: 'src/fonts/**/*',
    html: 'templates/**/*',
  },
};

// ================================================================
// BUILD
// ================================================================
gulp.task('build', () => {
  env.development = false;
  env.production = true;

  sequence(
    'clear',
    'fonts',
    'images',
    'js-admin',
    'js-admin-vendors',
    'js-common',
    'js-common-vendors',
    'js-pages',
    'styles-main',
    'styles-admin',
  );
});

// ================================================================
// Clear : Clear destination dir before build.
// ================================================================
gulp.task('clear', () => del(`${buildDir}/**/*`));

// ================================================================
// STYLES : Build common stylesheets
// ================================================================
gulp.task('styles-main', () => {
  gulp.src(path.src.styles.main)
    .pipe($.changed(path.build.styles, { extension: '.css' }))
    .pipe($.if(env.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.less({
      plugins: [lessGlob],
    }))
    .pipe($.if(env.production, $.autoprefixer()))
    .pipe($.rename({ suffix: '.min' }))
    .pipe($.if(env.production, $.cssnano()))
    .pipe($.if(env.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(path.build.styles))
    .pipe($.livereload());
});

gulp.task('styles-admin', () => {
  gulp.src(path.src.styles.admin)
    .pipe($.changed(path.build.styles, { extension: '.css' }))
    .pipe($.plumber())
    .pipe($.concat('admin.min.css'))
    .pipe($.if(env.production, $.autoprefixer()))
    .pipe($.if(env.production, $.cssnano()))
    .pipe(gulp.dest(path.build.styles))
    .pipe($.livereload());
});

// ================================================================
// JS : Helper functions
// ================================================================
function vendorJS(source, destination, fileName) {
  gulp.src(source)
    .pipe($.changed(path.build.js, { extension: '.js' }))
    .pipe($.concat(`${fileName}.js`))
    .pipe($.rename({ suffix: '.min' }))
    .pipe($.uglify())
    .pipe(gulp.dest(destination));
}

function appJS(source, destination, fileName) {
  gulp.src(source)
    .pipe($.changed(destination, { extension: '.js' }))
    .pipe($.if(env.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.concat(`${fileName}.js`))
    .pipe($.babel({
      presets: [babelPreset],
      compact: false,
    }))
    .pipe($.rename({ suffix: '.min' }))
    .pipe($.if(env.production, $.uglify()))
    .pipe($.if(env.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(destination))
    .pipe($.livereload());
}

// ================================================================
// JS : Build common js.
// ================================================================
gulp.task('js-common', () => {
  appJS(path.src.js.main, path.build.js, 'main');
});

// ================================================================
// JS : Build common vendors js only.
// ================================================================
gulp.task('js-common-vendors', () => {
  vendorJS(path.src.js.vendors, path.build.js, 'main-vendors');
});

// ================================================================
// JS : Build all pages scripts
// ================================================================
gulp.task('js-pages', () => {
  appJS(path.src.js.pages, path.build.js, 'pages');
});

// ================================================================
// JS : Build admin page scripts
// ================================================================
gulp.task('js-admin', () => {
  appJS(path.src.js.admin, path.build.js, 'admin');
});


// ================================================================
// JS : Build admin vendors js only
// ================================================================
gulp.task('js-admin-vendors', () => {
  vendorJS(path.src.js.adminVendors, path.build.js, 'admin-vendors');
});

// ================================================================
// Images : Copy images
// ================================================================
gulp.task('images', () => {
  gulp.src(path.src.images)
    .pipe($.changed(path.build.images))
    .pipe(gulp.dest(path.build.images));
});

// ================================================================
// Fonts : Copy fonts
// ================================================================
gulp.task('fonts', () => {
  gulp.src(path.src.fonts)
    .pipe($.changed(path.build.fonts))
    .pipe(gulp.dest(path.build.fonts));
});

// ================================================================
// WATCH
// ================================================================
gulp.task('watch', () => {
  $.livereload.listen();
  gulp.watch(path.watch.styles, [
    'styles-main',
    'styles-admin',
  ]);
  gulp.watch(path.watch.js, [
    'js-common',
    'js-pages',
    'js-admin',
  ]);
  gulp.watch(path.watch.images, ['images']);
  gulp.watch(path.watch.html, $.livereload.changed);
});

// ================================================================
// DEFAULT
// ================================================================
gulp.task('default', ['watch']);
