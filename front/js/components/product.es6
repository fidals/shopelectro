/**
 * Product Page module defines logic, operations and UI for ProductPage.
 */
const productModule = (function () {
  const DOM = {
    imageBig: $('#product-image-big'),
    addToBasketBtn: $('#btn-to-basket'),
    oneClickBuyEmail: $('#input-one-click-email'),
    oneClickBuyBtn: $('#btn-one-click-order'),
    counter: $('#product-count'),
    imagesToSwitch: $('.js-image-switch'),
    fancybox: $('.fancybox'),
  };

  let init = () => {
    setUpListeners();
    changeOneClickButtonState();
  };

  /**
   * Subscribing on events using mediator.
   */
  let setUpListeners = () => {
    DOM.imageBig.click(fancyBoxStart);
    DOM.imagesToSwitch.click(productImgSwitch);
    DOM.oneClickBuyEmail.keyup(changeOneClickButtonState);
    mediator.subscribe('onAddToBasket', addToBasket);
    DOM.addToBasketBtn.click(() => mediator.publish('onAddToBasket',
      {
        id: DOM.addToBasketBtn.attr('data-id'),
        count: DOM.counter.val(),
      }
    ));
    mediator.subscribe('onOneClickOrder', oneClickOrder);
    DOM.oneClickBuyBtn.click(() => mediator.publish('onOneClickOrder',
      {
        phone: DOM.oneClickBuyEmail.val(),
        count: DOM.counter.val(),
      }
    ));
  };

  /**
   * Initialize fancyBox on index image.
   */
  const fancyBoxStart = () => {
    let index = DOM.imageBig.attr('data-index');

    $.fancybox(
      DOM.fancybox, {
        index: index,
        helpers: {
          overlay: {
            locked: false,
          },
        },
      });

    return false;
  };

  /**
   * Adds product to basket.
   *
   * @param data.id - product's id
   * @param data.count - product's count
   */
  const addToBasket = (event, data) => {
    console.log(event);
    console.log(data);
  };

  /**
   * Phone validation on keypress
   */
  const changeOneClickButtonState = () => {
    if (!DOM.oneClickBuyEmail.length) return;
    const isFilled = isPhoneValid(DOM.oneClickBuyEmail.val());

    DOM.oneClickBuyBtn.attr('disabled', !isFilled);
  };

  /**
  * Handles one click order.
  *
  * @param data.phone - user phone
  * @param data.count - product count
  */
  const oneClickOrder = (event, data) => {
    console.log(data.phone);
    console.log(data.count);
  };

  /**
   * Переключение картинок товара:
   *
   * @param event - миниатюра, по которой был произведен клик;
   */
  const productImgSwitch = (event) => {
    let targetSrc = event.target.getAttribute('src');
    let dataIndex = event.target.getAttribute('data-index');

    if (targetSrc !== DOM.imageBig.attr('src')) {
      DOM.imageBig.attr({
        src: targetSrc,
        'data-index': dataIndex,
      });
    }
  };

  init();
}());
