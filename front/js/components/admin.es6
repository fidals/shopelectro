(() => {
  const DOM = {
    $productPage: $('.model-product'),
    $removeIcon: $('.js-remove-image'),
    $imageItem: $('.js-list-item'),
    searchFieldId: '#searchbar',
  };

  const config = {
    autocompleteURL: '/admin/autocomplete/',
    removeUrl: '/admin/remove-image/',
    minChars: 3,
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
    return new autoComplete({
      selector: DOM.searchFieldId,
      minChars: config.minChars,
      source: (term, response) => {
        $.getJSON(config.autocompleteURL, {
          q: term,
          pageType: getCurrentPageType(),
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
    return (DOM.$productPage.size() > 0) ? 'product' : 'category';
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
