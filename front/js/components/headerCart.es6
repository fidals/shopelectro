const headerCart = (() => {
  const DOM = {
    cart: $('.basket-parent'),
    reset: '.basket-reset',
    removeFromCart: '.js-basket-remove'
  };

  /**
   * Remove product with the given id from cart.
   * Trigger 'onCartUpdate' event afterwards.
   * @param productId
   */
  const remove = (productId) => removeFromCart(productId)
                                 .then((data) => mediator.publish('onCartUpdate', data));

  /**
   * Remove everything from cart.
   * Trigger 'onCartUpdate' event afterwards.
   */
  const clear = () => flushCart().then((data) => mediator.publish('onCartUpdate', data));


  /**
   * Render new cart's html.
   * @param event
   * @param data
   */
  const render = (event, data) => {
    DOM.cart.html(data['cart']);
  };
  
  const setUpListeners = () => {
    // Since product's list in cart dropdown is dynamic, we bind events on static parent
    DOM.cart.on('click', DOM.reset, () => clear());
    DOM.cart.on('click', DOM.removeFromCart, (event) => remove(event.target.getAttribute('id')));
    mediator.subscribe('onCartUpdate', render);
  };

  const init = () => setUpListeners();

  init();
})();
