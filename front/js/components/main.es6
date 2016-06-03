const mainPage = (() => {
  const DOM = {
    btnScrollTop: $('#btn-scroll-to-top'),
    scrollWrapper: $('#scroll-wrapper'),
    inputTouchspin: $('.js-touchspin')
  };

  const CONFIG = {
    touchspin: {
      min: 1,
      max: 10000,
      verticalbuttons: true,
      verticalupclass: 'glyphicon glyphicon-plus',
      verticaldownclass: 'glyphicon glyphicon-minus'
    },
    scrollbar: {
      autoReinitialise: true,
      mouseWheelSpeed: 30
    }
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
  };

  const setUpListeners = () => {
    $(window).scroll(toggleToTopBtn);
    DOM.btnScrollTop.on('click', () => $('html, body').animate({ scrollTop: 0 }, 300));
  };

  const pluginsInit = () => {
    DOM.scrollWrapper.jScrollPane(CONFIG.scrollbar);
    DOM.inputTouchspin.TouchSpin(CONFIG.touchspin);
  };

  const enableScrollToTop = () => {
    DOM.btnScrollTop.addClass('active');
  };

  const disableScrollToTop = () => {
    DOM.btnScrollTop.removeClass('active');
  };

  /**
   * Toggles to top button.
   */
  const toggleToTopBtn = () => {
    let isScreenBottom = $(window).scrollTop() > 300;

    if (isScreenBottom) {
      enableScrollToTop();
    } else {
      disableScrollToTop();
    }
  };

  init();
})();
