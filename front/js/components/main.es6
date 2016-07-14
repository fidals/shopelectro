const mainPage = (() => {
  const DOM = {
    $btnScrollTop: $('#btn-scroll-to-top'),
    $scrollWrapper: $('#scroll-wrapper'),
    $touchspin: $('.js-touchspin'),
    $timeTag: $('.js-select-time'),
    $phoneInputs: $('.js-masked-phone'),
  };

  const init = () => {
    fillInUserData({
      phone: localStorage.getItem(configs.LABELS.phone),
      time: localStorage.getItem(configs.LABELS.callTime),
    });
    setUpListeners();
  };

  /**
   * Fill in user stored data in inputs.
   */
  const fillInUserData = data => {
    if (data.phone) {
      $.each(DOM.$phoneInputs, (_, item) => $(item).val(data.phone));
    }
    if (data.time) {
      DOM.$timeTag.find(`[data-time=${data.time}]`).attr('selected', true);
    }
  };

  const setUpListeners = () => {
    $(window).scroll(toggleToTopBtn);
    DOM.$btnScrollTop.click(() => $('html, body').animate({ scrollTop: 0 }, 300));
  };

  const enableScrollToTop = () => {
    DOM.$btnScrollTop.addClass('active');
  };

  const disableScrollToTop = () => {
    DOM.$btnScrollTop.removeClass('active');
  };

  /**
   * Show\hide to top button.
   */
  const toggleToTopBtn = () => {
    ($(window).scrollTop() > 300) ? enableScrollToTop() : disableScrollToTop();
  };

  init();
})();
