const CONFIG = {
  autoComplete: {
    completeURL: '/search/autocomplete/',
    searchFieldId: '.js-search-input',
    minChars: 2,
  },
};

const autoComplete = new autoComplete({
  selector: CONFIG.autoComplete.searchFieldId,
  minChars: CONFIG.autoComplete.minChars,
  source: (term, response) => {
    $.getJSON(CONFIG.autoComplete.completeURL, {
      q: term,
    }, (namesArray) => {
      response(namesArray);
    });
  },
  renderItem: (item, search) => {
    search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
    return '<div class="autocomplete-suggestion" data-val="' + item + '">' + item.replace(re, "<b>$1</b>") + '</div>';
  },
});
