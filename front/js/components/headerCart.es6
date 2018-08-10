(() => {
  const DOM = {
    $cart: $('.js-cart-header'),
    orderTable: '#js-order-list',
    cartWrapper: '.js-cart-wrapper',
    resetCart: '.js-reset-cart',
    removeFromCart: '.js-cart-remove',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onCartUpdate', render, configs.initScrollbar, showCart);

    // Since product's list in Cart dropdown is dynamic, we bind events on static parent
    DOM.$cart.on('click', DOM.resetCart, clear);
    DOM.$cart.on('click', DOM.removeFromCart, remove);
  }

  /**
   * Remove product with the given id from cart.
   */
  function remove(event) {
    const productId = $(event.target).attr('data-id');
    const productCount = $(event.target).attr('data-count');

    server.removeFromCart(productId)
      .then((data) => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onProductRemove', [productId, productCount]);
      });
  }

  /**
   * Remove everything from cart.
   */
  function clear() {
    const productsData = $(DOM.removeFromCart).map((_, el) => {
      const $el = $(el);
      return {
        id: $el.attr('data-id'),
        quantity: $el.attr('data-count'),
      };
    }).get();
    server.flushCart()
      .then((data) => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onCartClear', [productsData]);
      });
  }

  /**
   * Perform header cart dropdown animation for every page, except order page.
   */
  function showCart() {
    if ($(DOM.orderTable).size() > 0) return;

    const $cartWrapper = $(DOM.cartWrapper);
    $cartWrapper.addClass('active');

    // timeout value now is under ux/ui experiments
    setTimeout(() => {
      $cartWrapper.removeClass('active');
    }, 5000);
  }

  /**
   * Render new Cart's html.
   * @param data
   */
  function render(_, data) {
    DOM.$cart.html(data.header);
  }

  init();
})();
