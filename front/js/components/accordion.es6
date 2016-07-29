const accordion = (() => {
  const itemKey = 'activeItem';
  const DOM = {
    $accordion: $('.js-accordion'),
    panels: $('.js-accordion-content'),
    titles: $('.js-accordion-title'),
    savedItem: $(`#${localStorage.getItem(itemKey)}`),
  };

  const init = () => {
    collapseAccordion();
    switchItem(DOM.savedItem);
    DOM.titles.click(event => switchItem($(event.target)));
  };

  /**
   * Case accordion item:
   *  -- active   - slide down it, make inactive
   *  -- inactive - slide up it, make active
   * @param $clickedItem - accordion item as jQuery object
   */
  const switchItem = $clickedItem => {
    if (!($clickedItem && accordionOnPage())) return;

    saveItem($clickedItem);

    if ($clickedItem.hasClass('active')) {
      collapseItem($clickedItem);
    } else {
      openItem($clickedItem);
    }
  };

  const accordionOnPage = () => DOM.$accordion.size();

  const openItem = $clickedItem => {
    collapseAccordion();
    $clickedItem
      .addClass('active')
      .next()
      .stop()
      .slideDown(100);
  };

  const collapseItem = $clickedItem => {
    $clickedItem
      .removeClass('active')
      .next()
      .stop()
      .slideUp(200);
    removeItem();
  };

  const saveItem = $item => {
    localStorage.setItem(itemKey, $item.attr('id'));
  };

  const removeItem = () => {
    localStorage.removeItem(itemKey);
  };

  const collapseAccordion = () => {
    DOM.titles.removeClass('active');
    DOM.panels.stop().slideUp();
  };

  init();
})();
