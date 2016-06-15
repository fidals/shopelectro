// ================================================================
// IMPORTS
// ================================================================
import gulp from 'gulp';
import changed from 'gulp-changed';
import gulpIf from 'gulp-if';
import babel from 'gulp-babel';
import less from 'gulp-less';
import autoprefixer from 'gulp-autoprefixer';
import lessGlob from 'less-plugin-glob';
import sourcemaps from 'gulp-sourcemaps';
import concat from 'gulp-concat';
import uglify from 'gulp-uglify';
import rename from 'gulp-rename';
import minifyCSS from 'gulp-cssnano';
import plumber from 'gulp-plumber';
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
        'front/js/vendors/jquery.mask.min.js',
        'front/js/vendors/bootstrap.min.js',
        'front/js/vendors/js.cookie.js',
        'front/js/vendors/jscrollpane.js',
        'front/js/vendors/jquery.bootstrap-touchspin.min.js',
      ],

      common: [
        'front/js/shared/*.es6',
        'front/js/components/main.es6',
      ],

      pages: [
        'front/js/vendors/bootstrap-select.js',
        'front/js/vendors/jquery.fancybox.min.js',
        'front/js/components/category.es6',
        'front/js/components/product.es6',
        'front/js/components/accordion.es6',
      ],

      admin: [
        'front/js/vendors/auto-complete.min.js',
        'front/js/components/admin.es6',
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
    styles: 'front/less/**/*.less',
    js: [
      'front/js/**/*',
    ],
    images: 'src/images/**/*.*',
    fonts: 'src/fonts/**/*.*',
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
    'js-common',
    'js-pages',
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
    .pipe(changed(PATH.build.styles, { extension: '.css' }))
    .pipe(gulpIf(ENV.development, sourcemaps.init()))
    .pipe(plumber())
    .pipe(less({
      plugins: [lessGlob],
    }))
    .pipe(gulpIf(ENV.production, autoprefixer({
      browsers: ['last 3 versions'],
    })))
    .pipe(rename({
      suffix: '.min',
    }))
    .pipe(gulpIf(ENV.production, minifyCSS()))
    .pipe(gulpIf(ENV.development, sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.styles));
});

// ================================================================
// JS : Build common vendors js only
// ================================================================
gulp.task('js-vendors', () => {
  gulp.src(PATH.src.js.vendors)
    .pipe(changed(PATH.build.js, { extension: '.js' }))
    .pipe(concat('vendors.js'))
    .pipe(rename({
      suffix: '.min',
    }))
    .pipe(uglify())
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build common scripts
// ================================================================
gulp.task('js-common', () => {
  gulp.src(PATH.src.js.common)
    .pipe(changed(PATH.build.js, { extension: '.js' }))
    .pipe(gulpIf(ENV.development, sourcemaps.init()))
    .pipe(plumber())
    .pipe(babel({
      presets: ['es2015'],
    }))
    .pipe(concat('main.js'))
    .pipe(rename({
      suffix: '.min',
    }))
    .pipe(gulpIf(ENV.production, uglify()))
    .pipe(gulpIf(ENV.development, sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build all pages scripts
// ================================================================
gulp.task('js-pages', () => {
  gulp.src(PATH.src.js.pages)
    .pipe(changed(PATH.build.js, { extension: '.js' }))
    .pipe(gulpIf(ENV.development, sourcemaps.init()))
    .pipe(plumber())
    .pipe(babel({
      presets: ['es2015'],
    }))
    .pipe(concat('pages.js'))
    .pipe(rename({
      suffix: '.min',
    }))
    .pipe(gulpIf(ENV.production, uglify()))
    .pipe(gulpIf(ENV.development, sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build admin page scripts
// ================================================================
gulp.task('js-admin', () => {
  gulp.src(PATH.src.js.admin)
    .pipe(changed(PATH.build.js, { extension: '.js' }))
    .pipe(gulpIf(ENV.development, sourcemaps.init()))
    .pipe(plumber())
    .pipe(babel({
      presets: ['es2015'],
    }))
    .pipe(concat('admin.js'))
    .pipe(rename({
      suffix: '.min',
    }))
    .pipe(gulpIf(ENV.production, uglify()))
    .pipe(gulpIf(ENV.development, sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// Images : Copy images
// ================================================================
gulp.task('build-imgs', () => {
  return gulp.src(PATH.src.images)
    .pipe(changed(PATH.build.images))
    .pipe(gulp.dest(PATH.build.images));
});

// ================================================================
// Fonts : Copy fonts
// ================================================================
gulp.task('build-fonts', () => {
  return gulp.src(PATH.src.fonts)
    .pipe(changed(PATH.build.fonts))
    .pipe(gulp.dest(PATH.build.fonts));
});

// ================================================================
// LiveReload
// ================================================================
// gulp.task('connect', () => {
// 	connect.server({
// 		root: 'dist',
// 		livereload : true
// 	});
// });

// ================================================================
// WATCH
// ================================================================
gulp.task('watch', () => {
  gulp.watch(PATH.watch.styles, ['styles']);
  gulp.watch(PATH.watch.js, ['js-common']);
  gulp.watch(PATH.watch.js, ['js-pages']);
  gulp.watch(PATH.watch.js, ['js-admin']);
});

// ================================================================
// DEFAULT
// ================================================================
gulp.task('default', ['watch']);
