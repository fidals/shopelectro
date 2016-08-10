const admin = (() => {
  const DOM = {
    $productPage: $('.model-product'),
    $removeIcon: $('.js-remove-image'),
    $imageItem: $('.js-list-item'),
    searchFieldId: '#searchbar',
    $sidebarToggle: $('.js-toggle-sidebar'),
  };

  const config = {
    sidebarStateKey: 'hiddenAdminSidebar',
    autocompleteURL: '/admin/autocomplete/',
    removeUrl: '/admin/remove-image/',
    minChars: 3,
  };

  const init = () => {
    setSidebarState();
    pluginsInit();
    setUpListeners();
  };

  function pluginsInit() {
    autoCompleteInit();
  }

  function setUpListeners() {
    DOM.$removeIcon.click(removeImage);
    DOM.$sidebarToggle.click(toggleSidebar);
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
   * Set sidebar state depending on stored key.
   */
  function setSidebarState() {
    if (isSidebarClosed()) {
      toggleSidebar();
    }
  }

  const isSidebarClosed = () => localStorage.getItem(config.sidebarStateKey) === '1';

  /**
   * Toggle admin sidebar & store it's state.
   */
  function toggleSidebar() {
    $('body').toggleClass('collapsed');
    localStorage.setItem(config.sidebarStateKey, isSidebarClosed() ? 0 : 1);
  }

  /**
   * Return current page type.
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
