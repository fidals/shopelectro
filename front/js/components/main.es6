const mainPage = (() => {
  const DOM = {
    btnScrollTop: $('#btn-scroll-to-top'),
    scrollWrapper: $('#scroll-wrapper'),
  };

  const CONFIG = {
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
