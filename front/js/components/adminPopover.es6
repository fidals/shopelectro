const popover = (() => {
  const messages = {
    noCategory: `Данной категории не существует.
                 Введите существующую категорию.`,
  };

  const className = '#popover';
  const settings = {
    animation: 'pop',
    backdrop: true,
    closeable: true,
    content: 'Content',
    placement: 'top',
    title: 'Title',
    width: 300,
  };

  /**
   * Show popover with extended settings.
   * @param offset - cell offset for popover offset calculating;
   */
  function showPopover(offset) {
    const extendedSettings = $.extend(
      {}, settings, {
        content: messages.noCategory,
        offsetTop: offset.top,
        offsetLeft: offset.left + (settings.width / 2),
        title: 'Ошибка',
      });

    $(`${className}`).webuiPopover('destroy').webuiPopover(extendedSettings);
    WebuiPopovers.show(`${className}`);
  }

  /**
   * Return cell offset for popover offset calculating.
   * @param $currentRow - last edited row;
   */
  function getPopoverOffset($currentRow) {
    const $cell = $currentRow.find('td[aria-describedby="jqGrid_category_name"]');

    return $cell.offset();
  }

  return {
    showPopover,
    getPopoverOffset,
  };
})();
