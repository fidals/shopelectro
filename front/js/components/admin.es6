const admin = (() => {
  const DOM = {
    categoryPage: $('.model-category'),
    productPage: $('.model-product'),
  };

  const CONFIG = {
    autoComplete: {
      completeURL: '/catalog/search/autocomplete/admin/',
      searchFieldId: '#searchbar',
      minChars: 3,
    },
  };


  let pageType = '';

  const search = new autoComplete({
    selector: CONFIG.autoComplete.searchFieldId,
    minChars: CONFIG.autoComplete.minChars,
    source: (term, response) => {
      $.getJSON(CONFIG.autoComplete.completeURL, {
        q: term,
        pageType: getCurrentPageType(),
      }, (namesArray) => {
        response(namesArray);
      });
    },
  });

  const getCurrentPageType = () => {
    if (DOM.productPage.size() > 0) {
      pageType = 'product';
    } else {
      pageType = 'category';
    }

    return pageType;
  };
})();
