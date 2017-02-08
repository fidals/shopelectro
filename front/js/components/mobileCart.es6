{
  const DOM = {
    cartQuantity: '.js-cart-size',
    cartPrice: '.js-mobile-cart-price',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', updateMobileCart);
  }

  /**
   * Update quantity and price.
   */
  function updateMobileCart(_, data) {
    $(DOM.cartQuantity).html(data.total_quantity);
    $(DOM.cartPrice).html(data.total_price);
  }

  init();
}
