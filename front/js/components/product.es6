const product = (() => {
  const DOM = {
    imageBig: $('#product-image-big'),
    imagesToSwitch: $('.js-image-switch'),
    fancybox: $('.fancybox'),
    addToCart: $('#btn-to-basket'),
    phone: $('#input-one-click-phone'),
    oneClick: $('#btn-one-click-order'),
    counter: $('#product-count')
  };

  const productId = () => DOM.addToCart.attr('data-id');

  const init = () => {
    setUpListeners();
    changeOneClickButtonState();
  };

  const setUpListeners = () => {
    DOM.imageBig.click(fancyBoxStart);
    DOM.imagesToSwitch.click(productImgSwitch);
    DOM.phone.keyup(changeOneClickButtonState);
    DOM.addToCart.click(() => buyProduct());
    DOM.oneClick.click(() => oneClick());
    mediator.subscribe('onOneClickBuy', successOrder);
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

  const oneClick = () => {
    const phone = DOM.phone.val();
    const count = DOM.counter.val();

    oneClickBuy(productId(), count, phone).then(() => mediator.publish('onOneClickBuy'));
  };

  /**
   * Phone validation on keypress
   */
  const changeOneClickButtonState = () => DOM.oneClick.attr('disabled', !isPhoneValid(DOM.phone.val()));

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

  const buyProduct = () => {
    let {id, count} = {
      id: productId(),
      count: DOM.counter.val()
    };

    addToCart(id, count).then((data) => mediator.publish('onCartUpdate', data));
  };

  const successOrder = () => location.href = '/shop/success-order';

  init();
})();

