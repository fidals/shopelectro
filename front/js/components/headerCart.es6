const headerCart = (() => {
  const DOM = {
    $cart: $('.js-cart-header'),
    resetCart: '.js-reset-cart',
    removeFromCart: '.js-cart-remove',
  };

  const init = () => {
    setUpListeners();
  };

  const setUpListeners = () => {
    mediator.subscribe('onCartUpdate', render);

    // Since product's list in cart dropdown is dynamic, we bind events on static parent
    DOM.$cart.on('click', DOM.resetCart, clear);
    DOM.$cart.on('click', DOM.removeFromCart, event => remove(event.target.getAttribute('id')));
  };

  /**
   * Remove product with the given id from cart.
   * @param productId
   */
  const remove = productId => server.removeFromCart(productId)
    .then(data => {
      mediator.publish('onCartUpdate', data);
      mediator.publish('onProductRemove');
    });

  /**
   * Remove everything from cart.
   */
  const clear = () => server.flushCart()
    .then(data => mediator.publish('onCartUpdate', data));

  /**
   * Render new cart's html.
   * @param event
   * @param data
   */
  const render = (event, data) => DOM.$cart.html(data.header);

  init();
})();
