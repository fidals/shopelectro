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
    completeURL: '/catalog/search/autocomplete/admin/',
    searchFieldId: '#searchbar',
    minChars: 3,
  };

  let pageType = '';

  const init = () => {
    setupXHR();
    search();
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

  const setUpListeners = () => {
    DOM.$removeIcon.click(removeImage);
  };

  const search = () => {
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

  const getCurrentPageType = () => {
    if (DOM.$productPage.size() > 0) {
      pageType = 'product';
    } else {
      pageType = 'category';
    }

    return pageType;
  };

  const removeImage = () => {
    const $target = $(event.target);

    $.post(
      UPLOAD.removeUrl, {
        csrfmiddlewaretoken: Cookies.get('csrftoken'),
        url: $target.data('id'),
      }
    ).success(() => $target.closest(DOM.$imageItem).slideUp());
  };

  init();
})();
