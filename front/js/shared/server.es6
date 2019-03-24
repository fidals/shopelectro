const server = (() => {  // Ignore ESLintBear (no-unused-vars)
  const config = {
    orderCallUrl: '/shop/order-call/',
    addToCartUrl: '/shop/cart-add/',
    oneClickBuyUrl: '/shop/one-click-buy/',
    changeCartUrl: '/shop/cart-change/',
    removeFromCartUrl: '/shop/cart-remove/',
    flushCartUrl: '/shop/cart-flush/',
    getCartUrl: '/shop/cart-get/',
    yandexOrderUrl: '/shop/yandex-order/',
    setViewTypeUrl: '/set-view-type/',
    saveFeedback: '/save-feedback/',
    deleteFeedback: '/delete-feedback/',
  };

  /**
   * Send information about order call.
   * @param phone
   * @param time
   * @param url
   */
  const sendOrderCall = (phone, time, url) => $.post(config.orderCallUrl, { phone, time, url });

  /**
   * Send Product feedback.
   */
  function sendFeedback(feedback) {
    return $.post({
      url: config.saveFeedback,
      data: {
        id: feedback.id,
        name: feedback.name,
        dignities: feedback.dignities,
        limitations: feedback.limitations,
        general: feedback.general,
        rating: feedback.rating,
      },
    });
  }

  const deleteFeedback = id => $.post(config.deleteFeedback, { id });

  /**
   * Load Products from server.
   * @param {string} url
   */
  const loadProducts = url => $.post(url);

  /**
   * Send viewType to store user's default view type.
   * @param event
   * @param viewType
   */
  const sendViewType = (event, viewType) => $.post(config.setViewTypeUrl, { view_type: viewType });

  /**
   * Add product to backend's Cart.
   * @param productId
   * @param quantity
   */
  function addToCart(productId, quantity) {
    return $.post(
      config.addToCartUrl,
      {
        product: productId,
        quantity,
      },
    );
  }

  /**
   * Flush (clear) the cart on backend.
   */
  const flushCart = () => $.post(config.flushCartUrl);

  /**
   * Handle one-click-buy feature. Sends:
   * @param product  - id of a bought product
   * @param quantity - selected quantity
   * @param phone    - customer's phone
   */
  function oneClickBuy(product, quantity, phone) {
    return $.post(config.oneClickBuyUrl, { product, quantity, phone });
  }

  /**
   * Remove given product from Cart.
   * @param productId
   */
  const removeFromCart = productId => $.post(config.removeFromCartUrl, { product: productId });

  /**
   * Return $.post request, which changes quantity of a given Product in Cart.
   * @param productId
   * @param quantity - new quantity of a product
   */
  function changeInCart(productId, quantity) {
    return $.post(
      config.changeCartUrl,
      {
        product: productId,
        quantity,
      },
    );
  }

  /**
   * Return $.get request, which gives Cart data.
   */
  function getCart() {
    return $.get(config.getCartUrl);
  }

  const sendYandexOrder = data => $.post(config.yandexOrderUrl, data);

  return {
    addToCart,
    changeInCart,
    deleteFeedback,
    getCart,
    loadProducts,
    flushCart,
    oneClickBuy,
    removeFromCart,
    sendFeedback,
    sendOrderCall,
    sendYandexOrder,
    sendViewType,
  };
})();
