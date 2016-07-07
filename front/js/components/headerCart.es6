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
    // Since product's list in cart dropdown is dynamic, we bind events on static parent
    DOM.$cart.on('click', DOM.resetCart, () => clear());
    DOM.$cart.on('click', DOM.removeFromCart, event => remove(event.target.getAttribute('id')));
    mediator.subscribe('onCartUpdate', render);
  };

  /**
   * Remove product with the given id from cart.
   * Trigger 'afterRemoveEvent' afterwards.
   * @param productId
   */
  const remove = productId => server.removeFromCart(productId)
    .then(data => afterRemoveEvent(data));

  /**
   * Remove everything from cart.
   * Trigger 'afterRemoveEvent' afterwards.
   */
  const clear = () => server.flushCart()
    .then(data => afterRemoveEvent(data));

  /**
   * Trigger 'onCartUpdate' event.
   */
  const afterRemoveEvent = (data) => {
      mediator.publish('onCartUpdate', data);
      yaCounter20644114.reachGoal('DELETE_PRODUCT');
    };

  /**
   * Render new cart's html.
   * @param event
   * @param data
   */
  const render = (event, data) => DOM.$cart.html(data.header);

  init();
})();
