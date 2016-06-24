const autocomplete = (() => {
  const CONFIG = {
    url: '/search/autocomplete/',
    searchInput: '.js-search-input',
    minChars: 2,
  };

  const highlight = (name, search) => {
    const prepared_search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const re = new RegExp("(" + prepared_search.split(' ').join('|') + ")", "gi");
    return name.replace(re, "<b>$1</b>");
  };

  const renderCatalogItem = (item, term) => {
    const context = {
      url: item.url,
      name: `<span>${highlight(item.name, term)}</span>`,
      price: item.price ? `<span>${item.price} руб.</span>` : '',
      itemName: item.name,
    };

    return `
      <div class="autocomplete-suggestion" data-val="${context.itemName}">
        <a href="${context.url}">${context.name}${context.price}</a>
      </div>
    `;
  };

  const renderLastItem = (item, term) => {
    const searchPageUrl = '/search/' + '?search=' + term;
    return `
      <div class="autocomplete-suggestion autocomplete-last-item">
        <a href="${searchPageUrl}">${item.name}</a>
      </div>
    `;
  };

  /**
   * Constructor args for autocomplete lib
   * https://goodies.pixabay.com/javascript/auto-complete/demo.html
   */
  const constructorArgs = {
    selector: CONFIG.searchInput,
    minChars: CONFIG.minChars,
    source: (term, response) => {
      $.getJSON(CONFIG.url, {
        q: term,
      }, (namesArray) => {
        response(namesArray);
      });
    },
    renderItem: (item, term) => {
      const possible_item_types = ['see_all', 'category', 'product'];
      console.assert(possible_item_types.includes(item.type));

      if (['category', 'product'].includes(item.type)) {
        return renderCatalogItem(item, term);
      }

      if (item.type === 'see_all') {
        return renderLastItem(item, term);
      }
    },
    onSelect: (event, term, item) => {
      const isRightClick = (event) => event.button === 2 || event.which === 3;
      if (isRightClick(event)) {
        return false;
      }
      window.location = $(item).find('a').attr('href');
    },
  };

  return {
    init: (autoComplete) => {
      new autoComplete(constructorArgs);
    }
  };

})();

autocomplete.init(autoComplete);
