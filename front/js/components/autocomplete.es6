const autocomplete = (() => {
  const CONFIG = {
    url: '/catalog/search/autocomplete/',
    searchInput: '.js-search-input',
    minChars: 2,
    itemsTypes: ['see_all', 'category', 'product'],
  };

  const init = () => {
    new autoComplete(constructorArgs);
  };

  /**
   * Highlight term in search results
   * Behind the scenes JavaScript autoComplete lib use this highlight code
   * Proof link: https://goodies.pixabay.com/javascript/auto-complete/demo.html
   *
   * @param name
   * @param search
   * @returns string
   */
  const highlight = (name, search) => {
    const preparedSearch = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const regexp = new RegExp("(" + preparedSearch.split(" ").join("|") + ")", "gi");
    return name.replace(regexp, "<b>$1</b>");
  };

  const renderItem = (item, term) => {
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
    // TODO: move on back side
    const searchPageUrl = `/catalog/search/?search=${term}`;
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
      console.assert(CONFIG.itemsTypes.includes(item.type));

      if (['category', 'product'].includes(item.type)) {
        return renderItem(item, term);
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

  init();
})();
