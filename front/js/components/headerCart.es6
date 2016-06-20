const headerCart = (() => {
  const DOM = {
    $cart: $('.js-cart-header'),
    $reset: '.js-reset-cart',
    $removeFromCart: '.js-cart-remove',
  };

  const init = () => {
    setUpListeners();
  };

  /**
   * Remove product with the given id from cart.
   * Trigger 'onCartUpdate' event afterwards.
   * @param productId
   */
  const remove = productId => server.removeFromCart(productId)
    .then(data => mediator.publish('onCartUpdate', data));

  /**
   * Remove everything from cart.
   * Trigger 'onCartUpdate' event afterwards.
   */
  const clear = () => server.flushCart().then(data => mediator.publish('onCartUpdate', data));

  /**
   * Render new cart's html.
   * @param event
   * @param data
   */
  const render = (event, data) => {
    DOM.$cart.html(data.header);
  };

  const setUpListeners = () => {
    // Since product's list in cart dropdown is dynamic, we bind events on static parent
    DOM.$cart.on('click', DOM.$reset, () => clear());
    DOM.$cart.on('click', DOM.$removeFromCart, event => remove(event.target.getAttribute('id')));
    mediator.subscribe('onCartUpdate', render);
  };

  init();
})();
