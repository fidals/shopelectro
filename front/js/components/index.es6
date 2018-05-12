(() => {
  const DOM = {
    $more_text_toggle: $('.js-more-text'),
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    DOM.$more_text_toggle.on('click', helpers.toggleText);
  }

  init();
})();
