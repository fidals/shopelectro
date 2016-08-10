// ================================================================
// IMPORTS
// ================================================================
const $ = require('gulp-load-plugins')();
import gulp from 'gulp';
import lessGlob from 'less-plugin-glob';
import sequence from 'run-sequence';

// ================================================================
// CONSTS
// ================================================================
const ENV = {
  development: true,
  production: false,
};

const PATH = {
  src: {
    styles: [
      'front/less/admin.less',
      'front/less/styles.less',
      'front/less/pages.less',
    ],

    js: {
      vendors: [
        'front/js/vendors/jquery-2.2.3.min.js',
        'front/js/vendors/bootstrap.min.js',
        'front/js/vendors/js.cookie.js',
        'front/js/vendors/jscrollpane.js',
        'front/js/vendors/jquery.mask.min.js',
        'front/js/vendors/jquery.bootstrap-touchspin.min.js',
        'front/js/vendors/auto-complete.min.js',
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
        'front/js/components/category.es6',
        'front/js/components/product.es6',
        'front/js/components/order.es6',
        'front/js/components/accordion.es6',
      ],

      adminVendors: [
        'front/js/vendors/jquery-ui.min.js',
        'front/js/vendors/jquery.slimscroll.min.js',
        'front/js/vendors/jqGrid.locale-ru.js',
        'front/js/vendors/jqGrid.min.js',
        'front/js/vendors/jstree.min.js',
      ],

      admin: [
        'front/js/components/admin.es6',
        'front/js/components/adminSidebar.es6',
        'front/js/components/jQgrid.es6',
      ],
    },

    images: 'front/images/**/*',
    fonts: 'front/fonts/**/*',
  },

  build: {
    styles: 'front/build/css/',
    js: 'front/build/js/',
    images: 'front/build/images/',
    fonts: 'front/build/fonts/',
  },

  watch: {
    styles: 'front/less/**/*',
    js: 'front/js/**/*',
    images: 'src/images/**/*',
    fonts: 'src/fonts/**/*',
    html: 'templates/**/*',
  },
};

// ================================================================
// BUILD
// ================================================================
gulp.task('build', (callback) => {
  ENV.development = false;
  ENV.production = true;

  sequence(
    'styles',
    'js-vendors',
    'js-main',
    'js-pages',
    'js-admin-vendors',
    'js-admin',
    'build-imgs',
    'build-fonts',
    callback
  );
});

// ================================================================
// STYLES : Build common stylesheets
// ================================================================
gulp.task('styles', () => {
  gulp.src(PATH.src.styles)
    .pipe($.changed(PATH.build.styles, { extension: '.css' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.less({
      plugins: [lessGlob],
    }))
    .pipe($.if(ENV.production, $.autoprefixer({
      browsers: ['last 3 versions'],
    })))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.cssnano()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.styles))
    .pipe($.livereload());
});

// ================================================================
// JS : Build common vendors js only
// ================================================================
gulp.task('js-vendors', () => {
  gulp.src(PATH.src.js.vendors)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.concat('vendors.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.uglify())
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build main scripts
// ================================================================
gulp.task('js-main', () => {
  gulp.src(PATH.src.js.main)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.babel({
      presets: ['es2015'],
      compact: false,
    }))
    .pipe($.concat('main.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.uglify()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js))
    .pipe($.livereload());
});

// ================================================================
// JS : Build all pages scripts
// ================================================================
gulp.task('js-pages', () => {
  gulp.src(PATH.src.js.pages)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.babel({
      presets: ['es2015'],
      compact: false,
    }))
    .pipe($.concat('pages.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.uglify()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build admin vendors js only
// ================================================================
gulp.task('js-admin-vendors', () => {
  gulp.src(PATH.src.js.adminVendors)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.concat('admin-vendors.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.uglify())
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build admin page scripts
// ================================================================
gulp.task('js-admin', () => {
  gulp.src(PATH.src.js.admin)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.babel({
      presets: ['es2015'],
    }))
    .pipe($.concat('admin.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.uglify()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// Images : Copy images
// ================================================================
gulp.task('build-imgs', () => {
  gulp.src(PATH.src.images)
    .pipe($.changed(PATH.build.images))
    .pipe(gulp.dest(PATH.build.images));
});

// ================================================================
// Fonts : Copy fonts
// ================================================================
gulp.task('build-fonts', () => {
  gulp.src(PATH.src.fonts)
    .pipe($.changed(PATH.build.fonts))
    .pipe(gulp.dest(PATH.build.fonts));
});

// ================================================================
// WATCH
// ================================================================
gulp.task('watch', () => {
  $.livereload.listen();
  gulp.watch(PATH.watch.styles, ['styles']);
  gulp.watch(PATH.watch.js, ['js-main', 'js-pages', 'js-admin']);
  gulp.watch(PATH.watch.images, ['images']);
  gulp.watch(PATH.watch.html, $.livereload.changed);
});

// ================================================================
// DEFAULT
// ================================================================
gulp.task('default', ['watch']);
