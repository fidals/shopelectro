const autocomplete = (() => {
  const config = {
    url: '/search/autocomplete/',
    searchInput: '.js-search-input',
    minChars: 2,
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
    const regexp = new RegExp(`(${preparedSearch.split(' ').join('|')})`, 'gi');
    return name.replace(regexp, '<b>$1</b>');
  };

  const renderSearchItem = (item, term) => {
    const context = {
      url: item.url,
      name: `<span>${highlight(item.name, term)}</span>`,
      price: item.price ? `<span>${item.price} руб.</span>` : '',
    };

    // Do not change string template here cause of issue.
    // https://github.com/Pixabay/JavaScript-autoComplete/issues/39
    return `<div class="autocomplete-suggestion" data-val="${term}">
      <a href="${context.url}">${context.name}${context.price}</a>
    </div>`;
  };

  const renderLastItem = (item) => {
    // Do not change string template here cause of issue.
    // https://github.com/Pixabay/JavaScript-autoComplete/issues/39
    return `<div class="autocomplete-suggestion autocomplete-last-item">
       <a href="${item.url}">${item.name}</a>
    </div>`;
  };

  /**
   * Constructor args for autocomplete lib.
   * Packed into a function because search input selector should be
   * rendered before autocomplete will init
   * https://goodies.pixabay.com/javascript/auto-complete/demo.html
   */
  const getAutoCompleteArgs = () => {
    return {
      selector: $(config.searchInput)[0],
      source: (term, response) => {
        $.getJSON(config.url, {term}, (searchedItems) => {
          response(searchedItems);
        });
      },
      renderItem: (item, term) => {
        if (['category', 'product'].includes(item.type)) {
          return renderSearchItem(item, term);
        }

        if (item.type === 'see_all') {
          return renderLastItem(item);
        }
      },
      onSelect: (event, term, item) => {
        event.preventDefault();
        const isRightClick = event.button === 2 || event.which === 3;
        if (isRightClick) return;

        window.location = $(item).find('a').attr('href');
      }
    };
  };

  const init = () => {
    new autoComplete(getAutoCompleteArgs());
  };

  init();

  return {
    init,
  };
})();
