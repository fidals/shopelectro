import autoprefixer from 'autoprefixer';
import babelPreset from 'babel-preset-es2015';
import csso from 'postcss-csso';
import del from 'del';
import gulp from 'gulp';
import lessGlob from 'less-plugin-glob';
import mqpacker from 'css-mqpacker';
import sequence from 'run-sequence';

const $ = require('gulp-load-plugins')();
const flexibility = require('postcss-flexibility')();
const spawnSync = require('child_process').spawnSync;

console.log(`
You've seen warning because of deprecated deps during npm install.
It's recursive deps of actual packages, that we are using.
So, it's nothing we can do.
`)

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
  const pythonPackagesPath = process.env.DEPS_DIR;
  return require(`${pythonPackagesPath}/${appName}/front/paths.js`);
}

// ================================================================
// CONSTS
// ================================================================
const env = {
  development: true,
  production: false,
};

const plugins = [
  autoprefixer(),
  csso(),
  mqpacker({
    sort: true,
  }),
];

const buildDir = 'build';
const ecommercePaths = getAppSrcPaths('ecommerce');
const genericAdminPaths = getAppSrcPaths('generic_admin');

const path = {
  src: {
    sprites: {
      main: 'front/images/spriteSrc/main/*.png',
    },

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
        'front/js/vendors/jquery.mmenu.min.js',
        'front/js/vendors/js.cookie.js',
        'front/js/vendors/jscrollpane.js',
        'front/js/vendors/jquery.mask.min.js',
        'front/js/vendors/jquery.bootstrap-touchspin.min.js',
        'front/js/vendors/autocomplete.min.js',
        'front/js/vendors/bootstrap-select.js',
        'front/js/vendors/jquery.fancybox.min.js',
      ],

      main: [
        ecommercePaths.trackers,
        'front/js/shared/*.es6',
        'front/js/components/orderCall.es6',
        'front/js/components/headerCart.es6',
        'front/js/components/mobileCart.es6',
        'front/js/components/mobileMenu.es6',
        'front/js/components/main.es6',
        'front/js/components/autocomplete.es6',
      ],

      index: [
        'front/js/components/index.es6',
      ],

      pages: [
        'front/js/components/category.es6',
        'front/js/components/categoryFilters.es6',
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

      vendorsIE: [
        'front/js/vendors/html5shiv.min.js',
        'front/js/vendors/flexibility.js',
      ],
    },

    images: [
      'front/images/**/*',
      genericAdminPaths.img,
    ],

    fonts: 'front/fonts/**/*',
  },

  build: {
    sprites: {
      pathInCss: '../images',
      less: {
        main: 'front/less/common/utilities',
      },
      images: 'front/images/',
    },
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
      ecommercePaths.watch,
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
    'clear', [
      'fonts',
      'js-admin',
      'js-admin-vendors',
      'js-common',
      'js-common-vendors',
      'js-index',
      'js-pages',
      'js-ie-vendors',
      'styles-main',
      'styles-admin',
      'styles-ie',
    ],
    'images',
  );
});

// ================================================================
// Clear : Clear destination directory.
// ================================================================
gulp.task('clear', () => del(`${buildDir}/**/*`, { force: true }));

// ================================================================
// STYLES
// ================================================================
gulp.task('styles-main', () => {
  gulp.src(path.src.styles.main)
    .pipe($.changed(path.build.styles, { extension: '.css' }))
    .pipe($.if(env.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.less({ plugins: [lessGlob] }))
    .pipe($.if(env.production, $.postcss(plugins)))
    .pipe($.rename({ suffix: '.min' }))
    .pipe($.if(env.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(path.build.styles))
    .pipe($.livereload());
});

gulp.task('styles-admin', () => {
  gulp.src(path.src.styles.admin)
    .pipe($.changed(path.build.styles, { extension: '.css' }))
    .pipe($.plumber())
    .pipe($.concat('admin.min.css'))
    .pipe($.if(env.production, $.postcss(plugins)))
    .pipe(gulp.dest(path.build.styles))
    .pipe($.livereload());
});

gulp.task('styles-ie', () => {
  gulp.src(path.src.styles.main)
    .pipe($.less({ plugins: [lessGlob] }))
    .pipe($.concat('ie.min.css'))
    .pipe($.postcss([...plugins, flexibility]))
    .pipe(gulp.dest(path.build.styles));
});

// ================================================================
// JS : Helper functions.
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
// JS : Build common index js only.
// ================================================================
gulp.task('js-index', () => {
  appJS(path.src.js.index, path.build.js, 'index');
});

// ================================================================
// JS : Build all pages js.
// ================================================================
gulp.task('js-pages', () => {
  appJS(path.src.js.pages, path.build.js, 'pages');
});

// ================================================================
// JS : Build admin page js only.
// ================================================================
gulp.task('js-admin', () => {
  appJS(path.src.js.admin, path.build.js, 'admin');
});


// ================================================================
// JS : Build admin vendors js only.
// ================================================================
gulp.task('js-admin-vendors', () => {
  vendorJS(path.src.js.adminVendors, path.build.js, 'admin-vendors');
});

// ================================================================
// JS : Build vendors js for IE.
// ================================================================
gulp.task('js-ie-vendors', () => {
  vendorJS(path.src.js.vendorsIE, path.build.js, 'ie-vendors');
});

// ================================================================
// Images: Sprites.
// ================================================================
gulp.task('sprites', () => {
  sequence(
    'generate-sprites',
    'images',
  );
});

gulp.task('generate-sprites', () => {
  const spriteData = gulp.src(path.src.sprites.main)
    .pipe($.spritesmith({
      imgName: 'sprite-main.png',
      cssName: 'sprite-main.less',
      imgPath: `${path.build.sprites.pathInCss}/sprite-main.png`,
      padding: 2,
    }));
  spriteData.img.pipe(gulp.dest(path.build.sprites.images));
  spriteData.css
    .pipe(gulp.dest(path.build.sprites.less.main));
});

// ================================================================
// Images : Optimize and copy images.
// ================================================================
gulp.task('images', () => {
  gulp.src(path.src.images)
    .pipe($.changed(path.build.images))
    .pipe($.imagemin())
    .pipe(gulp.dest(path.build.images));
});

// ================================================================
// Fonts : Copy fonts.
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
    'js-index',
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
