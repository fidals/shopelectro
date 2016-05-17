const DOM = {
  categoryPage: $('.model-category'),
  productPage: $('.model-product'),
};

const CONFIG = {
  autoComplete: {
    completeURL: '/admin-autocomplete/',
    searchFieldId: '#searchbar',
    minChars: 3,
  },
  page: '',
};

let autoComplete = new autoComplete({
  selector: CONFIG.autoComplete.searchFieldId,
  minChars: CONFIG.autoComplete.minChars,
  source: (term, response) => {
    if (DOM.productPage.size() > 0) {
      CONFIG.page = 'product';
    } else {
      CONFIG.page = 'category';
    }

    $.getJSON(CONFIG.autoComplete.completeURL, {
      q: term,
      page: CONFIG.page,
    }, (namesArray) => {
      response(namesArray);
    });
  },
});
