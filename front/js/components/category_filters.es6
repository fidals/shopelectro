{
  const DOM = {
    $loadMoreBtn: $('#btn-load-products'),
    $filtersApplyBtn: $('.js-apply-filter'),
    $filterTitle: $('.js-toggle-tag-section'),
    $filtersWrapper: $('.js-tags-inputs'),
    $filtersClearBtn: $('.js-clear-tag-filter'),
  };

  const filtersStorageKey = 'hiddenFilters';

  const config = {
    hiddenFilters: getHiddenFilters(),
    filterGroup: 'data-tag-group',
  };

  const init = () => {
    setUpListeners();
    setUpFilters();
    setUpFiltersSections();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    DOM.$filtersApplyBtn.click(loadFilteredProducts);
    DOM.$filterTitle.click(toggleFilterSection);
    DOM.$filtersClearBtn.click(clearFilters);
    DOM.$filtersWrapper.on('click', 'input', toggleApplyBtnState);
  }

  function getHiddenFilters() {
    const str = localStorage.getItem(filtersStorageKey);
    return str ? str.split(',') : [];
  }

  const getFilterQueryParam = () => window.location.search.split('tags=')[1];

  /**
   * Reloads current page with `tags` query parameter.
   */
  function loadFilteredProducts() {
    const tags = [];

    DOM.$filtersWrapper.map((_, item) => {
      const $checkedItems = $(item).find('input:checked');

      $checkedItems.map((_, checkedItem) => {
        tags.push($(checkedItem).data('tag-id'));
      });
    });

    window.location.href = `${DOM.$loadMoreBtn.data('url')}?tags=${tags}`;
  }

  /**
   * Toggle apply filter btn active\disabled state based on
   * checked\unchecked checkboxes.
   */
  function toggleApplyBtnState() {
    const inputsArr = Array.from(DOM.$filtersWrapper.find('input'));
    const isSomeChecked = inputsArr.some(item => item.checked === true);

    DOM.$filtersApplyBtn.attr('disabled', !isSomeChecked);
  }

  /**
   * Store filter sections state set by user.
   */
  function storeFilterSectionState(index) {
    if (config.hiddenFilters.includes(index)) {
      const removeIndex = config.hiddenFilters.indexOf(index);
      config.hiddenFilters.splice(removeIndex, 1);
    } else {
      config.hiddenFilters.push(index);
    }

    localStorage.setItem(filtersStorageKey, config.hiddenFilters);
  }

  /**
   * Toggle filter sections.
   */
  function toggleFilterSection() {
    const $this = $(this);
    const targetClass = 'opened';

    if ($this.hasClass(targetClass)) {
      $this.removeClass(targetClass);
    } else {
      $this.addClass(targetClass);
    }

    $this.next().slideToggle();
    storeFilterSectionState($this.attr(`${config.filterGroup}`));
  }

  /**
   * Set up filter checkboxes based on query `tags` parameter.
   */
  function setUpFilters() {
    if (!window.location.search) return;

    // /?tags=3,4 => ['3', '4']
    const activeFilterIds = getFilterQueryParam().split(',');

    activeFilterIds.map(item => $(`#tag-${item}`).attr('checked', true));
    toggleApplyBtnState();
  }

  /**
   * Set up filter sections toggle state based on localStorage.
   */
  function setUpFiltersSections() {
    if (!config.hiddenFilters.length) return;

    config.hiddenFilters.forEach((index) => {
      DOM.$filterTitle.filter(`[${config.filterGroup}=${index}]`).next().slideUp();
    });
  }

  /**
   * Clear all checked filters.
   */
  function clearFilters() {
    $.each(
      DOM.$filtersWrapper.find('input'),
      (_, input) => $(input).attr('checked', false),
    );

    window.location.href = DOM.$loadMoreBtn.data('url');
  }

  init();
}
