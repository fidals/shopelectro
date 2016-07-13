const mainPage = (() => {
  const DOM = {
    $btnScrollTop: $('#btn-scroll-to-top'),
    $scrollWrapper: $('#scroll-wrapper'),
    $touchspin: $('.js-touchspin'),
  };

  // TODO: maybe we should move all the configs into separate file.
  // http://youtrack.stkmail.ru/issue/dev-748
  const CONFIG = {
    scrollbar: {
      autoReinitialise: true,
      mouseWheelSpeed: 30,
    },
    touchspin: {
      min: 1,
      max: 10000,
      verticalbuttons: true,
      verticalupclass: 'glyphicon glyphicon-plus',
      verticaldownclass: 'glyphicon glyphicon-minus',
    },
    fancybox: {
      openEffect: 'fade',
      closeEffect: 'elastic',
      helpers: {
        overlay: {
          locked: false,
        },
      },
    },
  };

  const init = () => {
    pluginsInit();
    setupXHR();
    setUpListeners();
  };

  // TODO: move to config module
  // http://youtrack.stkmail.ru/issue/dev-748
  const setupXHR = () => {
    const csrfUnsafeMethod = (method) => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    const token = Cookies.get('csrftoken');

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', token);
        }
      },
    });
  };

  const setUpListeners = () => {
    $(window).scroll(toggleToTopBtn);
    DOM.$btnScrollTop.click(() => $('html, body').animate({ scrollTop: 0 }, 300));
  };

  const pluginsInit = () => {
    DOM.$scrollWrapper.jScrollPane(CONFIG.scrollbar);
    DOM.$touchspin.TouchSpin(CONFIG.touchspin);
  };

  const enableScrollToTop = () => {
    DOM.$btnScrollTop.addClass('active');
  };

  const disableScrollToTop = () => {
    DOM.$btnScrollTop.removeClass('active');
  };

  /**
   * Toggle to top button.
   */
  const toggleToTopBtn = () => {
    ($(window).scrollTop() > 300) ? enableScrollToTop() : disableScrollToTop();
  };

  init();
})();
