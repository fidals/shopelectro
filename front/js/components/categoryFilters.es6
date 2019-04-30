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
    filterGroup: 'tag-group',
    isCollapseInversed: $('.js-tags-list').data('default-collapse'),
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
    DOM.$filterTitle.click(toggleClickedGroup);
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
    const tagsByGroups = tags.reduce((group, item) => {
      const groupId = item.group;
      group[groupId] = group[groupId] || [];  // Ignore ESLintBear (no-param-reassign)
      group[groupId].push(item.slug);
      return group;
    }, {});

    return Object.keys(tagsByGroups).reduce((previous, current) => {
      const delim = previous ? TAGS_GROUP_DELIMITER : '';
      return previous + delim + tagsByGroups[current].join(TAGS_TYPE_DELIMITER);
    }, '');
  }

  function parseTags(string) {
    return [].concat(...(
      string.split(TAGS_GROUP_DELIMITER).map(group => group.split(TAGS_TYPE_DELIMITER))
    ));
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
      config.hiddenFilterGroupIds = config.hiddenFilterGroupIds.filter(i => i !== index);
    } else {
      config.hiddenFilterGroupIds.push(index);
    }

    localStorage.setItem(filtersStorageKey, config.hiddenFilterGroupIds);
  }

  /**
   * Toggle filter groups.
   */
  function toggleGroup($group) {
    const targetClass = 'opened';

    if ($group.hasClass(targetClass)) {
      $group.removeClass(targetClass);
    } else {
      $group.addClass(targetClass);
    }

    $group.next().slideToggle();
  }

  function toggleClickedGroup() {
    const $group = $(this);
    toggleGroup($group);
    storeFilterGroupState($group.data(config.filterGroup));
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
   * Set up filter group toggle state based on localStorage and collapse mode.
   */
  function setUpFilterGroups() {
    if (config.isCollapseInversed) {
      DOM.$filterTitle.each((_, e) => toggleGroup($(e)));
    }
    if (!config.hiddenFilterGroupIds.length) return;
    config.hiddenFilterGroupIds.forEach((index) => {
      const $el = DOM.$filterTitle.filter(`[data-${config.filterGroup}=${index}]`);
      toggleGroup($el);
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
