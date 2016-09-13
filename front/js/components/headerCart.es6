(() => {
  const DOM = {
    $cart: $('.js-cart-header'),
    cartWrapper: '.js-cart-wrapper',
    resetCart: '.js-reset-cart',
    removeFromCart: '.js-cart-remove',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', render);

    // Since product's list in cart dropdown is dynamic, we bind events on static parent
    DOM.$cart.on('click', DOM.resetCart, clear);
    DOM.$cart.on('click', DOM.removeFromCart, remove);
  }

  /**
   * Remove product with the given id from cart.
   */
  function remove() {
    const productId = $(event.target).attr('data-id');

    server.removeFromCart(productId)
      .then(data => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onProductRemove');
      });
  }

  /**
   * Remove everything from cart.
   */
  function clear() {
    server.flushCart()
      .then(data => mediator.publish('onCartUpdate', data));
  }

  function showCart() {
    const $cartWrapper = $(DOM.cartWrapper);
    $cartWrapper.addClass('active');
    setTimeout(() => {
      $cartWrapper.removeClass('active');
    }, 3000);
  }

  /**
   * Render new cart's html.
   * @param data
   */
  function render(_, data) {
    DOM.$cart.html(data.header);
    configs.scrollbarReinit();
    showCart();
  }

  init();
})();
