(() => {
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

  const TAGS_TYPE_DELIMITER = '-or-';
  const TAGS_GROUP_DELIMITER = '-and-';

  function serializeTags(tags) {
    var tags_by_groups = new Map(),
        slugs_groups = [];

    tags.map(item => tags_by_groups.set(item.group, []));
    tags.map(item => tags_by_groups.get(item.group).push(item.slug));

    for (var [_, slugs] of tags_by_groups) {
      slugs_groups.push(
        slugs.join(TAGS_TYPE_DELIMITER)
      );
    };
    return slugs_groups.join(TAGS_GROUP_DELIMITER);
  }

  function parseTags(string) {
    return [].concat(...(
      string.split(TAGS_GROUP_DELIMITER).map(group => group.split(TAGS_TYPE_DELIMITER))
    ))
  }

  /**
   * Reloads current page with `tags` query parameter.
   */
  function loadFilteredProducts() {
    const $tagsObject = DOM.$filtersWrapper
      .find('input:checked')
      .map((_, checkedItem) => (
        {
            slug: $(checkedItem).data('tag-slug'),
            group: $(checkedItem).data('tag-group-id'),
        }
      ));
    const tags = serializeTags(Array.from($tagsObject));

    window.location.href = `${DOM.$loadMoreBtn.data('url')}tags/${tags}/`;

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
    // /tags/от-сети-220-в-and-брелок/ => ['от-сети-220-в', 'брелок']
    const activeFilterIds = parseTags(helpers.getUrlEndpointParam('tags'));

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
   * Reload page without `tags` query parameters.
   */
  function clearFilters() {
    $.each(
      DOM.$filtersWrapper.find('input'),
      (_, input) => $(input).attr('checked', false),
    );

    window.location.href = helpers.removeUrlEndpoint('tags');
  }

  init();
})();
