(() => {
  const DOM = {
    $btnScrollTop: $('#btn-scroll-to-top'),
    $menuItem: $('.js-menu-item'),
    $phoneInput: $('.js-masked-phone'),
    $searchExampleText: $('#search-example-text'),
    $searchInput: $('.js-search-input'),
    $timeTag: $('.js-select-time'),
  };

  const init = () => {
    fillInUserData({
      phone: localStorage.getItem(configs.labels.phone),
      time: localStorage.getItem(configs.labels.callTime),
    });
    setUpListeners();
    initSlider();
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
    window.addEventListener(
      'resize',
      helpers.debounce(() => initSlider(), 200),
    );
  }

  function initSlider() {
    const $toSlick = $('.tile-about .row');
    const $slicked = $('.tile-about .slick-initialized');

    if ($(window).width() < configs.screenSizes.sm) {
      $toSlick.slick({
        dots: true,
        arrows: true,
        mobileFirst: true,
      });
    } else if ($slicked.length) {
      $slicked.slick('unslick');
    }
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
