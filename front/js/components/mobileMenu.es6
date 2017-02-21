{
  const DOM = {
    $mobCatalogBtn: $('.js-mobile-catalog-btn'),
    $mobLinkArrow: $('.js-mobile-link-arrow'),
    $mobMenuToggler: $('.js-mobile-menu-toggler'),
    $mobSearch: $('.mm-search').find('input'),
    searchClass: 'js-search-input',
  };

  const mmenuApi = configs.$menu.data('mmenu');

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    DOM.$mobCatalogBtn.click(toggleCatalogAccordion);
    DOM.$mobLinkArrow.click(toggleSubCatalog);
    DOM.$mobMenuToggler.click(toggleMenuIcon);
    mmenuApi.bind('opening', initSearch);
    mmenuApi.bind('closing', toggleMenuIcon);
  }

  function initSearch() {
    if (DOM.$mobSearch.hasClass(DOM.searchClass)) return;
    DOM.$mobSearch.addClass(DOM.searchClass);
    autocomplete.init();
  }

  function toggleMenuIcon() {
    DOM.$mobMenuToggler.toggleClass('open');
  }

  function toggleSubCatalog(event) {
    event.preventDefault();
    event.stopPropagation();
    const $subList = $(this).parent().next();

    if ($subList.is(':visible')) {
      $(this).removeClass('opened');
      $subList.slideUp('opened');
    } else {
      $(this).addClass('opened');
      $subList.slideDown('opened');
    }
  }

  function toggleCatalogAccordion() {
    $(this).toggleClass('opened');

    const $list = $(this).next();
    if ($list.is(':visible')) {
      $list.stop().slideUp();
    } else {
      $list.stop().slideDown();
    }
  }

  init();
}
