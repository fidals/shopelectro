(() => {
  const DOM = {
    $pageType: document.location.pathname.split('/').slice(-2, -1)[0],
    $removeIcon: $('.js-remove-image'),
    $imageItem: $('.js-list-item'),
    searchFieldId: '#searchbar',
  };

  const config = {
    autocompleteURL: '/admin/autocomplete/',
    removeUrl: '/admin/remove-image/',
    minChars: 3,
    pagesType: ['product', 'category'],
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
  };

  function pluginsInit() {
    autoCompleteInit();
  }

  function setUpListeners() {
    DOM.$removeIcon.click(removeImage);
  }

  function autoCompleteInit() {
    const currentType = getCurrentPageType();
    if (!currentType) {
      return;
    }

    return new autoComplete({
      selector: DOM.searchFieldId,
      minChars: config.minChars,
      source: (term, response) => {
        $.getJSON(config.autocompleteURL, {
          q: term,
          pageType: currentType,
        }, namesArray => {
          response(namesArray);
        });
      },
    });
  }

  /**
   * Return current entity page type.
   */
  function getCurrentPageType() {
    const [currentPageType] = config.pagesType.filter((type) => type === DOM.$pageType);
    return currentPageType;
  }

  /**
   * Remove entity image.
   */
  function removeImage() {
    const $target = $(event.target);

    $.post(config.removeUrl, { url: $target.data('id') })
      .success(() => $target.closest(DOM.$imageItem).slideUp());
  }

  init();
})();
