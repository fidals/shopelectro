const admin = (() => {
  const DOM = {
    $productPage: $('.model-product'),
    $removeIcon: $('.js-remove-image'),
    $imageItem: $('.js-list-item'),
    searchFieldId: '#searchbar',
  };

  const CONFIG = {
    removeUrl: '/admin/remove-image/',
    completeURL: '/admin/autocomplete/',
    minChars: 3,
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
  };

  const pluginsInit = () => {
    autoCompleteInit();
  };

  const autoCompleteInit = () => {
    return new autoComplete({
      selector: DOM.searchFieldId,
      minChars: CONFIG.minChars,
      source: (term, response) => {
        $.getJSON(CONFIG.completeURL, {
          q: term,
          pageType: getCurrentPageType(),
        }, namesArray => {
          response(namesArray);
        });
      },
    });
  };

  const setUpListeners = () => {
    DOM.$removeIcon.click(removeImage);
  };

  function getCurrentPageType() {
    return (DOM.$productPage.size() > 0) ? 'product' : 'category';
  }

  const removeImage = () => {
    const $target = $(event.target);

    $.post(
      CONFIG.removeUrl, {
        url: $target.data('id'),
      }
    )
    .success(() => $target.closest(DOM.$imageItem).slideUp());
  };

  init();
})();
