const admin = (() => {
  const DOM = {
    $sortableList: $('#sortable'),
    $hideFilterBtn: $('.js-hide-filter'),
    $filterWrapper: $('.js-filter-wrapper'),
    $filterCheckbox: $('.js-filter-checkbox'),
    $saveFiltersBtn: $('.js-save-filters'),
    $dropFiltersBtn: $('.js-drop-filters'),
    sortableClass: 'js-sortable-item',
    searchFieldId: '#searchbar',
  };

  const config = {
    autocompleteURL: '/admin/autocomplete/',
    minChars: 3,
    currentPageType: document.location.pathname.split('/').slice(-2, -1)[0],
    pagesType: {'categorypage': 'category', 'productpage': 'product'},
    showText: 'Показать фильтр полей',
    hideText: 'Скрыть фильтр полей',
  };

  const filterStateKey = 'isFilterVisible';
  const filterFieldsKey = 'filterFields';

  const init = () => {
    pluginsInit();
    setUpListeners();
    mediator.publish('onFiltersPrepare');
  };

  function pluginsInit() {
    autoCompleteInit();
  }

  function setUpListeners() {
    mediator.subscribe('onFiltersPrepare', setFiltersState, prepareFilters, initFilters);
    mediator.subscribe('onFiltersSave', saveFilters, reloadPage);
    DOM.$saveFiltersBtn.click(() => mediator.publish('onFiltersSave'));

    DOM.$hideFilterBtn.click(toggleFilters);
    DOM.$dropFiltersBtn.click(dropFilters);
    DOM.$filterCheckbox.change(updateSortFields);
  }

  function autoCompleteInit() {
    const currentType = getCurrentPageType();
    if (!currentType) return;

    return new autoComplete({
      selector: DOM.searchFieldId,
      minChars: config.minChars,
      source: (term, response) => {
        $.getJSON(config.autocompleteURL, {
          term,
          pageType: currentType,
        }, namesArray => {
          response(namesArray);
        });
      },
    });
  }

  /**
   * Return current entity page type.
   */
  function getCurrentPageType() {
    return config.pagesType[config.currentPageType];
  }

  /**
   * Filter fields logic below.
   */
  function setFiltersState() {
    if (localStorage.getItem(filterStateKey) === 'true') {
      DOM.$hideFilterBtn.html(config.hideText);
      DOM.$filterWrapper.slideToggle();
    }
  }

  function prepareFilters() {
    const storedFields = getStoredFilterKey();
    let fieldsHtml = '';

    if (storedFields) {
      clearCheckboxes();
      fieldsHtml = renderCustomFilters(storedFields);
    } else {
      fieldsHtml = renderStandardFilters();
    }

    DOM.$sortableList.html(fieldsHtml);
  }

  function renderStandardFilters() {
    let fieldsHtml = '';

    for (const field of getCheckedCheckboxes()) {
      const id = $(field).attr('id');
      const text = $(field).prev().text();

      fieldsHtml += `
        <li class="sortable-item ${DOM.sortableClass}" data-name="${id}">${text}</li>
      `;
    }

    return fieldsHtml;
  }

  function renderCustomFilters(storedFields) {
    const fields = JSON.parse(storedFields);
    let fieldsHtml = '';

    for (const field of fields) {
      const $inputToCheck = $(`#${field}`);
      const filterText = $inputToCheck.prev().text();

      $inputToCheck.prop('checked', true);
      fieldsHtml += `
        <li class="sortable-item ${DOM.sortableClass} ui-sortable-handle" data-name="${field}">
          ${filterText}
        </li>
      `;
    }

    return fieldsHtml;
  }

  function initFilters() {
    DOM.$sortableList
      .sortable({
        placeholder: 'sortable-item ui-state-highlight',
      })
      .disableSelection();
  }

  function clearCheckboxes() {
    $.each(DOM.$filterCheckbox, (_, item) => $(item).prop('checked', false));
  }

  function getCheckedCheckboxes() {
    return DOM.$filterCheckbox.filter((_, item) => $(item).is(':checked'));
  }

  function updateSortFields() {
    const filterName = $(event.target).attr('id');
    const filterText = $(event.target).prev().text();
    const $filterField = DOM.$sortableList.find(`.${DOM.sortableClass}`)
      .filter(`[data-name=${filterName}]`);

    if ($(event.target).is(':checked')) {
      DOM.$sortableList.append(`
        <li class="sortable-item ${DOM.sortableClass}" data-name="${filterName}">${filterText}</li>
      `);
    } else {
      $filterField.remove();
    }
  }

  function saveFilters() {
    const fields = [];

    $.each($(`.${DOM.sortableClass}`), (_, item) => {
      fields.push($(item).attr('data-name'));
    });

    localStorage.setItem(filterFieldsKey, JSON.stringify(fields));
  }

  function dropFilters() {
    localStorage.removeItem(filterFieldsKey);
    reloadPage();
  }

  function toggleFilters() {
    const $self = $(event.target);

    if (DOM.$filterWrapper.is(':visible')) {
      $self.html(config.showText);
      localStorage.setItem(filterStateKey, 'false');
    } else {
      $self.html(config.hideText);
      localStorage.setItem(filterStateKey, 'true');
    }

    DOM.$filterWrapper.slideToggle();
  }

  function reloadPage() {
    location.reload();
  }

  const getStoredFilterKey = () => localStorage.getItem(filterFieldsKey);

  init();

  return {
    getCheckedCheckboxes,
    getStoredFilterKey,
  };
})();
