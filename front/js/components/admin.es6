const admin = (() => {
  const DOM = {
    $productPage: $('.model-product'),
    $removeIcon: $('.js-remove-image'),
    $imageItem: $('.js-list-item'),
    searchFieldId: '#searchbar',
    $sidebarToggle: $('.js-toggle-sidebar'),
  };

  const CONFIG = {
    storageKey: 'hiddenAdminSidebar',
    removeUrl: '/admin/remove-image/',
    completeURL: '/admin/autocomplete/',
    minChars: 3,
  };

  const init = () => {
    setSidebarState();
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
    DOM.$sidebarToggle.click(toggleSidebar);
    DOM.$sidebarToggle.click(storeSidebarState);
  };

  function setSidebarState() {
    if (isSidebarClosed()) {
      toggleSidebar();
    }
  }

  const isSidebarClosed = () => localStorage.getItem(CONFIG.storageKey) === '1';

  function getCurrentPageType() {
    return (DOM.$productPage.size() > 0) ? 'product' : 'category';
  }

  const removeImage = () => {
    const $target = $(event.target);

    $.post(CONFIG.removeUrl, { url: $target.data('id') })
      .success(() => $target.closest(DOM.$imageItem).slideUp());
  };

  const toggleSidebar = () => {
    $('body').toggleClass('collapsed');
  };

  const storeSidebarState = () => {
    localStorage.setItem(CONFIG.storageKey, isSidebarClosed() ? 0 : 1);
  };

  init();
})();
