(() => {
  const DOM = {
    $btnScrollTop: $('#btn-scroll-to-top'),
    $menuItem: $('.js-menu-item'),
    $phoneInput: $('.js-masked-phone'),
    $searchExampleText: $('#search-example-text'),
    $searchInput: $('.js-search-input'),
    $timeTag: $('.js-select-time'),
  };

  // @todo #903:30m  Move SCREENS const to configs.es6 file.

  // variables.less contains the same values
  const SCREENS = {
    xs: 480,
    sm: 768,
    md: 992,
    lg: 1200,
  };

  const init = () => {
    if ($(window).width() < SCREENS.sm) {
      $('.tile-about .row').slick({
        dots: true,
        arrows: true,
        mobileFirst: true,
      });
    }

    fillInUserData({
      phone: localStorage.getItem(configs.labels.phone),
      time: localStorage.getItem(configs.labels.callTime),
    });
    setUpListeners();
  };

  /**
   * Fill inputs by user's stored data.
   */
  function fillInUserData(data) {
    if (data.phone) {
      $.each(DOM.$phoneInput, (_, item) => $(item).val(data.phone));
    }
    if (data.time) {
      DOM.$timeTag.find(`[data-time=${data.time}]`).attr('selected', true);
    }
  }

  function setUpListeners() {
    $(window).scroll(toggleToTopBtn);
    DOM.$searchExampleText.click(pasteSearchExampleText);
    DOM.$btnScrollTop.click(scrollToTop);
    DOM.$menuItem.hover(
      helpers.debounce(toggleSubmenu(true), 200),
      toggleSubmenu(false),
    );
  }

  function scrollToTop() {
    $('html, body').animate({ scrollTop: 0 }, 300);
  }

  const enableScrollToTop = () => DOM.$btnScrollTop.addClass('active');
  const disableScrollToTop = () => DOM.$btnScrollTop.removeClass('active');

  /**
   * Show\hide `To top` button.
   */
  function toggleToTopBtn() {
    if ($(window).scrollTop() > 300) {
      enableScrollToTop();
    } else {
      disableScrollToTop();
    }
  }

  /**
   * Paste search example text in search input.
   */
  function pasteSearchExampleText() {
    const searchExampleText = DOM.$searchExampleText.text().trim();
    $(DOM.$searchInput).val(searchExampleText).focus();
  }

  /**
   * Show\hide navigation list on hover with user friendly delay.
   */
  function toggleSubmenu(show) {
    return function toggler() {
      const $el = $(this);
      const isHovered = $el.is(':hover');
      const action = show && isHovered ? 'addClass' : 'removeClass';
      $el[action]('hovered');
    };
  }

  init();
})();
