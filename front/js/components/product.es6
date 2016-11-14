{
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

  function setUpListeners() {
    mediator.subscribe('onOneClickBuy', successOrder);

    DOM.$imageBig.click(fancyBoxStart);
    DOM.$imagesToSwitch.click(productImgSwitch);
    DOM.$addToCart.click(buyProduct);
    DOM.$oneClick.click(oneClick);
    DOM.$phone.keyup(changeOneClickButtonState);
  }

  /**
   * Initialize fancyBox on specific index image.
   */
  function fancyBoxStart() {
    $.fancybox(
      DOM.$fancybox, {
        index: DOM.$imageBig.attr('data-index'),
        helpers: {
          overlay: {
            locked: false,
          },
        },
      });

    return false; // this return is required
  }

  /**
   * Send product data & redirect page.
   */
  function oneClick() {
    helpers.disableSubmit(DOM.$oneClick, 'Ожидайте...');

    server.oneClickBuy(productId(), DOM.$counter.val(), DOM.$phone.val())
      .then(() => mediator.publish('onOneClickBuy'));
  }

  /**
   * Change button disable state.
   */
  function changeOneClickButtonState() {
    if (DOM.$oneClick.size() > 0) {
      DOM.$oneClick.attr('disabled', !helpers.isPhoneValid(DOM.$phone.val()));
    }
  }

  /**
   * Switch product images.
   *
   * @param event - click on image preview;
   */
  function productImgSwitch(event) {
    const targetSrc = $(event.target).attr('src');
    const dataIndex = $(event.target).attr('data-index');

    if (targetSrc !== DOM.$imageBig.attr('src')) {
      DOM.$imageBig.attr({
        src: targetSrc,
        'data-index': dataIndex,
      });
    }
  }

  function buyProduct() {
    const { id, count } = {
      id: productId(),
      count: DOM.$counter.val(),
    };

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  function successOrder() {
    location.href = '/shop/order-success';
  }

  init();
}
