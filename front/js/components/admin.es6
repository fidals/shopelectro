const admin = (() => {
  const DOM = {
    $productPage: $('.model-product'),
    $removeIcon: $('.js-remove-image'),
    $imageItem: $('.js-list-item'),
  };

  const UPLOAD = {
    $: $('.js-file-input'),
    removeUrl: '/admin/remove-image/',
  };

  const AUTOCOMPLETE = {
    completeURL: '/admin/autocomplete/',
    searchFieldId: '#searchbar',
    minChars: 3,
  };

  const init = () => {
    pluginsInit();
    setupXHR();
    setUpListeners();
  };

  // TODO: move to config module
  // http://youtrack.stkmail.ru/issue/dev-748
  const setupXHR = () => {
    const csrfUnsafeMethod = (method) => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    const token = Cookies.get('csrftoken');

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', token);
        }
      },
    });
  };

  const pluginsInit = () => {
    return new autoComplete({
      selector: AUTOCOMPLETE.searchFieldId,
      minChars: AUTOCOMPLETE.minChars,
      source: (term, response) => {
        $.getJSON(AUTOCOMPLETE.completeURL, {
          q: term,
          pageType: getCurrentPageType(),
        }, (namesArray) => {
          response(namesArray);
        });
      },
    });
  };

  const setUpListeners = () => {
    DOM.$removeIcon.click(removeImage);
  };

  const getCurrentPageType = () => {
    return (DOM.$productPage.size() > 0) ? 'product' : 'category';
  };

  const removeImage = () => {
    const $target = $(event.target);

    $.post(
      UPLOAD.removeUrl, {
        url: $target.data('id'),
      }
    )
    .success(() => $target.closest(DOM.$imageItem).slideUp());
  };

  init();
})();
