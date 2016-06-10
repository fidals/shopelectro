const accordion = (() => {

  let getSavedItem = () => $('#' + localStorage.getItem(ITEM_KEY));

  const ITEM_KEY = 'activeItem';
  const DOM = {
    panels: $('.js-accordion-content'),
    titles: $('.js-accordion-title'),
    savedItem: getSavedItem(),
  };

  let init = () => {
    collapseAccordion();
    switchItem(DOM.savedItem);
    DOM.titles.click((event) => switchItem($(event.target)));
  };

  /**
   * Case accordion item:
   *  -- active - slide down it, make inactive
   *  -- inactive - slide up it, make active
   * @param $clickedItem - accordion item as jQuery object
   */
  let switchItem = ($clickedItem) => {
    if (!$clickedItem) {
      return
    }

    saveItem($clickedItem);

    if ($clickedItem.hasClass('active')) {
      collapseItem($clickedItem);
    } else {
      openItem($clickedItem);
    }
  };

  let openItem = ($clickedItem) => {
    let $to_switch = $clickedItem.next();
    collapseAccordion();
    $clickedItem.addClass('active');
    $to_switch.stop().slideDown();
  };

  let collapseItem = ($clickedItem) => {
    let $to_switch = $clickedItem.next();
    $clickedItem.removeClass('active');
    $to_switch.stop().slideUp();
    removeItem();
  };

  let saveItem = ($item) => {
    localStorage.setItem(ITEM_KEY, $item.attr('id'));
  };

  let removeItem = ($item) => {
    localStorage.removeItem(ITEM_KEY);
  };

  let collapseAccordion = () => {
    DOM.titles.removeClass('active');
    DOM.panels.stop().slideUp();
  };

  init();
})();
