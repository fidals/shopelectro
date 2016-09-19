const product = (() => {
  const DOM = {
    $imageBig: $('#product-image-big'),
    $imagesToSwitch: $('.js-image-switch'),
    $fancybox: $('.fancybox'),
    $addToCart: $('#btn-to-basket'),
    $phone: $('#input-one-click-phone'),
    $oneClick: $('#btn-one-click-order'),
    $counter: $('#product-count'),
  };

  const productId = () => DOM.$addToCart.attr('data-id');

  const init = () => {
    setUpListeners();
    changeOneClickButtonState();
  };

  const setUpListeners = () => {
    mediator.subscribe('onOneClickBuy', successOrder);

    DOM.$imageBig.click(fancyBoxStart);
    DOM.$imagesToSwitch.click(productImgSwitch);
    DOM.$addToCart.click(buyProduct);
    DOM.$oneClick.click(oneClick);
    DOM.$phone.keyup(changeOneClickButtonState);
  };

  /**
   * Initialize fancyBox on specific index image.
   */
  const fancyBoxStart = () => {
    $.fancybox(
      DOM.$fancybox, {
        index: DOM.$imageBig.attr('data-index'),
        helpers: {
          overlay: {
            locked: false,
          },
        },
      });

    return false;
  };

  /**
   * Send product data & redirect page.
   */
  const oneClick = () => {
    server.oneClickBuy(productId(), DOM.$counter.val(), DOM.$phone.val())
      .then(() => mediator.publish('onOneClickBuy'));
  };

  /**
   * Change button disable state.
   */
  const changeOneClickButtonState = () => {
    if (DOM.$oneClick.size() > 0) {
      DOM.$oneClick.attr('disabled', !helpers.isPhoneValid(DOM.$phone.val()));
    }
  };

  /**
   * Switch product images.
   *
   * @param event - click on image preview;
   */
  const productImgSwitch = event => {
    const targetSrc = $(event.target).attr('src');
    const dataIndex = $(event.target).attr('data-index');

    if (targetSrc !== DOM.$imageBig.attr('src')) {
      DOM.$imageBig.attr({
        src: targetSrc,
        'data-index': dataIndex,
      });
    }
  };

  const buyProduct = () => {
    const { id, count } = {
      id: productId(),
      count: DOM.$counter.val(),
    };

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', data));
  };

  function successOrder() {
    location.href = '/shop/success-order';
  }

  init();
})();
