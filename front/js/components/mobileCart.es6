(() => {
  const DOM = {
    $mobileCart: $('.js-mobile-cart'),
    cartQuantity: '.js-cart-size',
    cartPrice: '.js-mobile-cart-price',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', toggleCart, updateCart);
  }

  /**
   * Show\hide mobile cart on adding\removing Products.
   */
  function toggleCart(_, data) {
    const html = data.html || data;
    if (html.total_quantity > 0) {
      DOM.$mobileCart.removeClass('hidden');
    } else {
      DOM.$mobileCart.addClass('hidden');
    }
  }

  /**
   * Update quantity and price.
   */
  function updateCart(_, data) {
    $(DOM.cartQuantity).html(data.total_quantity);
    $(DOM.cartPrice).html(data.total_price);
  }

  init();
})();
