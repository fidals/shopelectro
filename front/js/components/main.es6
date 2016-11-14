(() => {
  const DOM = {
    $btnScrollTop: $('#btn-scroll-to-top'),
    $touchspin: $('.js-touchspin'),
    $timeTag: $('.js-select-time'),
    $phoneInputs: $('.js-masked-phone'),
    $searchExampleText: $('#search-example-text'),
    $searchInput: $('.js-search-input'),
  };

  const init = () => {
    fillInUserData({
      phone: localStorage.getItem(configs.labels.phone),
      time: localStorage.getItem(configs.labels.callTime),
    });
    setUpListeners();
  };

  /**
   * Fill in user stored data in inputs.
   */
  function fillInUserData(data) {
    if (data.phone) {
      $.each(DOM.$phoneInputs, (_, item) => $(item).val(data.phone));
    }
    if (data.time) {
      DOM.$timeTag.find(`[data-time=${data.time}]`).attr('selected', true);
    }
  }

  function setUpListeners() {
    $(window).scroll(toggleToTopBtn);
    DOM.$searchExampleText.click(pasteSearchExampleText);
    DOM.$btnScrollTop.click(() => $('html, body').animate({ scrollTop: 0 }, 300));
  }

  const enableScrollToTop = () => {
    DOM.$btnScrollTop.addClass('active');
  };

  const disableScrollToTop = () => {
    DOM.$btnScrollTop.removeClass('active');
  };

  /**
   * Show\hide to top button.
   */
  function toggleToTopBtn() {
    ($(window).scrollTop() > 300) ? enableScrollToTop() : disableScrollToTop();
  }

  /**
   * Paste search example text in search input.
   */
  function pasteSearchExampleText() {
    const searchText = DOM.$searchExampleText.text().trim();

    $(DOM.$searchInput).val(searchText).focus();
  }

  init();
})();
