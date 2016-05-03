// ================================================================
// REQUIRES
// ================================================================
var gulp = require('gulp');
var babel = require('gulp-babel');
var	less = require('gulp-less');
var autoprefixer = require('gulp-autoprefixer');
var	sourcemaps = require('gulp-sourcemaps');
var	concat = require('gulp-concat');
var	uglify = require('gulp-uglify');
var	rename = require('gulp-rename');
var	minifyCSS = require('gulp-cssnano');
var	plumber = require('gulp-plumber');
var	sequence = require('run-sequence');

// ================================================================
// BUILD
// ================================================================
gulp.task('build', function(callback) {
  sequence(
    'styles',
    'js-vendors',
    'js-common',
    'img-copy',
    'fonts-copy',
    callback
  );
});

// ================================================================
// STYLES : Build common stylesheets
// ================================================================
gulp.task('styles', function() {
  gulp.src([
    './front/less/styles.less',
  ])
  .pipe(sourcemaps.init())
  .pipe(plumber())
  .pipe(less())
  .pipe(autoprefixer({
    browsers: ['last 3 versions']
  }))
  .pipe(rename({
    suffix: '.min'
  }))
  .pipe(minifyCSS())
  .pipe(sourcemaps.write('.'))
  .pipe(gulp.dest('./front/build/css')
  );
});

// ================================================================
// JS : Build common vendors js only
// ================================================================
gulp.task('js-vendors', function() {
  gulp.src([
    './front/js/vendors/jquery-2.2.3.min.js',
    './front/js/vendors/jquery.mask.min.js',
    './front/js/vendors/bootstrap.min.js',
    './front/js/vendors/jscrollpane.js',
  ])
    .pipe(concat('vendors.js'))
    .pipe(rename({
      suffix: '.min'
    }))
    .pipe(uglify())
    .pipe(gulp.dest('./front/build/js'));
});

// ================================================================
// JS : Build common scripts
// ================================================================
gulp.task('js-common', function() {
  gulp.src([
    './front/js/server.es6',
    './front/js/main.es6',
  ])
    .pipe(sourcemaps.init())
    .pipe(plumber())
    .pipe(babel({
      presets: ['es2015']
    }))
    .pipe(concat('main.js'))
    .pipe(rename({
      suffix: '.min'
    }))
    .pipe(uglify())
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest('./front/build/js'));
});

// ================================================================
// Images : Copy images
// ================================================================
gulp.task('img-copy', function() {
  return gulp.src('./front/images/**/*')
    .pipe(gulp.dest('./front/build/images'));
});

// ================================================================
// Fonts : Copy fonts
// ================================================================
gulp.task('fonts-copy', function() {
  return gulp.src('./front/fonts/**/*')
    .pipe(gulp.dest('./front/build/fonts'));
});

// ================================================================
// LiveReload
// ================================================================
// gulp.task('connect', function() {
// 	connect.server({
// 		root: 'dist',
// 		livereload : true
// 	});
// });

// ================================================================
// WATCH
// ================================================================
gulp.task('watch', function() {
	gulp.watch('./front/less/**/*.less', ['styles']);
	gulp.watch('./front/js/*.es6', ['js-common']);
});

// ================================================================
// DEFAULT
// ================================================================
gulp.task('default', ['watch']);
