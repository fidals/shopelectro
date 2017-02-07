{
  const DOM = {
    $loadMoreBtn: $('#btn-load-products'),
    $filtersApplyBtn: $('.js-apply-filter'),
    $filterTitle: $('.js-toggle-tag-group'),
    $filtersWrapper: $('.js-tags-inputs'),
    $filtersClearBtn: $('.js-clear-tag-filter'),
  };

  const filtersStorageKey = 'hiddenFilterGroupIds';

  const config = {
    hiddenFilterGroupIds: getHiddenFilterGroupIds(),
    filterGroup: 'data-tag-group',
  };

  const init = () => {
    setUpListeners();
    setUpFilters();
    setUpFilterGroups();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    DOM.$filtersApplyBtn.click(loadFilteredProducts);
    DOM.$filterTitle.click(toggleFilterGroup);
    DOM.$filtersClearBtn.click(clearFilters);
    DOM.$filtersWrapper.on('click', 'input', toggleApplyBtnState);
  }

  function getHiddenFilterGroupIds() {
    const str = localStorage.getItem(filtersStorageKey);
    return str ? str.split(',') : [];
  }

  /**
   * Reloads current page with `tags` query parameter.
   */
  function loadFilteredProducts() {
    const $tagsObject = DOM.$filtersWrapper
      .find('input:checked')
      .map((_, checkedItem) => $(checkedItem).data('tag-id'));
    const tags = Array.from($tagsObject);

    window.location.href = `${DOM.$loadMoreBtn.data('url')}?tags=${tags}`;
  }

  /**
   * Toggle apply filter btn active\disabled state based on
   * checked\unchecked checkboxes.
   */
  function toggleApplyBtnState() {
    const checkboxesArr = Array.from(DOM.$filtersWrapper.find('input'));
    const isSomeChecked = checkboxesArr.some(item => item.checked === true);

    DOM.$filtersApplyBtn.attr('disabled', !isSomeChecked);
  }

  /**
   * Store filter groups state set by user.
   */
  function storeFilterGroupState(index) {
    if (config.hiddenFilterGroupIds.includes(index)) {
      const removeIndex = config.hiddenFilterGroupIds.indexOf(index);
      config.hiddenFilterGroupIds.splice(removeIndex, 1);
    } else {
      config.hiddenFilterGroupIds.push(index);
    }

    localStorage.setItem(filtersStorageKey, config.hiddenFilterGroupIds);
  }

  /**
   * Toggle filter groups.
   */
  function toggleFilterGroup() {
    const $group = $(this);
    const targetClass = 'opened';

    if ($group.hasClass(targetClass)) {
      $group.removeClass(targetClass);
    } else {
      $group.addClass(targetClass);
    }

    $group.next().slideToggle();
    storeFilterGroupState($group.attr(`${config.filterGroup}`));
  }

  /**
   * Set up filter checkboxes based on query `tags` parameter.
   */
  function setUpFilters() {
    if (!window.location.search) return;

    // /?tags=3,4 => ['3', '4']
    const activeFilterIds = helpers.getUrlParam('tags').split(',');

    activeFilterIds.map(item => $(`#tag-${item}`).attr('checked', true));
    toggleApplyBtnState();
  }

  /**
   * Set up filter group toggle state based on localStorage.
   */
  function setUpFilterGroups() {
    if (!config.hiddenFilterGroupIds.length) return;

    config.hiddenFilterGroupIds.forEach((index) => {
      DOM.$filterTitle.filter(`[${config.filterGroup}=${index}]`).next().slideUp();
    });
  }

  /**
   * Clear all checked filters.
   * Reset tags query parameters.
   * Reload page.
   */
  function clearFilters() {
    $.each(
      DOM.$filtersWrapper.find('input'),
      (_, input) => $(input).attr('checked', false),
    );

    window.location.href = helpers.removeQueryParam('tags');
  }

  init();
}
