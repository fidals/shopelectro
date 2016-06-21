const CONFIG = {
  autoComplete: {
    completeURL: '/search/autocomplete/',
    searchField: '.js-search-input',
    minChars: 2,
  },
};

const autoComplete = new autoComplete({
  selector: CONFIG.autoComplete.searchField,
  minChars: CONFIG.autoComplete.minChars,
  source: (term, response) => {
    $.getJSON(CONFIG.autoComplete.completeURL, {
      q: term,
    }, (namesArray) => {
      response(namesArray);
    });
  },
  renderItem: (item, search) => {
    const highlight = (name, search) => {
      const prepared_search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
      const re = new RegExp("(" + prepared_search.split(' ').join('|') + ")", "gi");
      return name.replace(re, "<b>$1</b>");
    };

    const searchPageUrl = '/search/' + '?search=' + search;
    const lastItemHtml = `
      <div class="autocomplete-suggestion">
        <a class="ui-corner-all" href="${searchPageUrl}">${item.name}</a>
      </div>
    `;
    if (item.type && item.type === 'see_all') { return lastItemHtml; }

    const context = {
      url: item.url,
      name: `<span>${highlight(item.name, search)}</span>`,
      price: item.price ? `<span>${item.price} руб.</span>` : '',
      itemName: item.name,
    };
    const itemHtml = `
      <div class="autocomplete-suggestion" data-val="${context.itemName}">
        <a class="ui-corner-all" href="${context.url}">${context.name}${context.price}</a>
      </div>
    `;
    return itemHtml;
  },
  onSelect: (event, term, item) => {
    const isRightClick = (event) => event.button === 2 || event.which === 3;
    if (isRightClick(event)) { return false; }
    window.location = $(item).find('a').attr('href');
  },
});
