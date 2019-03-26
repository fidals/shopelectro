(() => {
  const DOM = {
    $copyPhoneTag: $('.js-copy-phone'),
    $copyEmailTag: $('.js-copy-mail'),
    $backcallModal: $('.js-backcall-order'),
    $searchForm: $('.js-search-form'),
    $btnToCartProductPage: $('.js-to-cart-on-product-page'),
    $btnToCartCategoryPage: $('.js-product-to-cart'),
    $cartHeader: $('.js-cart-header'),
    goToCartLink: '.js-go-to-cart',
    $removeFromCart: $('.js-remove'),
    $goToProductLink: $('.js-browse-product'),
    $downloadPrice: $('.js-download-price'),
    $downloadPriceInFooter: $('.js-download-price-footer'),
    $purchasedOrder: $('.js-purchased-order'),
  };

  // @todo #759:60m Create tests for eCommerce tracking.
  //  Test all events, these perform tracking operations.

  // Sync container for yaTracker
  window.dataLayer = window.dataLayer || [];
  const loadedGa = loadGaTransport('gtm_loaded');  // Ignore ESLintBear (no-undef)
  const yaTracker = new YATracker(window.dataLayer, 'RUB');  // Ignore ESLintBear (no-undef)
  const gaTracker = new GATracker(loadedGa, 'ecommerce');  // Ignore ESLintBear (block-scoped-var)

  const init = () => {
    setUpListeners();
    publishPurchase();
  };

  function setUpListeners() {
    mediator.subscribe('onOneClickBuy', () => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FAST_BUY_SEND');
    });
    mediator.subscribe('onOrderSend', () => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FULL_BUY_SEND');
    });
    mediator.subscribe('onCartClear', (_, products) => {
      yaTracker.remove(products);
    });
    // We receive an onProductAdd event from a category and a product pages
    mediator.subscribe('onProductAdd', (_, data) => {
      yaTracker.add([data]);
    });
    mediator.subscribe('onProductRemove', (_, data) => {
      reachGoal('DELETE_PRODUCT');
      yaTracker.remove([data]);
    });
    mediator.subscribe('onProductDetail', (_, data) => yaTracker.detail([data]));
    mediator.subscribe('onBackCallSend', () => reachGoal('BACK_CALL_SEND'));

    DOM.$searchForm.submit(() => reachGoal('USE_SEARCH_FORM'));
    DOM.$removeFromCart.click(() => reachGoal('DELETE_PRODUCT'));
    DOM.$cartHeader.on('click', DOM.goToCartLink, () => reachGoal('CART_OPEN'));
    DOM.$backcallModal.click(() => reachGoal('BACK_CALL_OPEN'));
    DOM.$goToProductLink.click(() => reachGoal('PROD_BROWSE'));
    DOM.$downloadPrice.click(() => reachGoal('PRICE_HEADER'));
    DOM.$downloadPriceInFooter.click(() => reachGoal('PRICE_FOOTER'));
    DOM.$btnToCartProductPage
      .click(() => {
        reachGoal('PUT_IN_CART_FROM_PRODUCT');
        reachGoal('CMN_PUT_IN_CART');
      });
    DOM.$btnToCartCategoryPage
      .click(() => {
        reachGoal('PUT_IN_CART_FROM_CATEGORY');
        reachGoal('CMN_PUT_IN_CART');
      });
  }

  function publishPurchase() {
    if (!DOM.$purchasedOrder.length) return;
    const orderData = {
      id: DOM.$purchasedOrder.data('id'),
      revenue: parseFloat(DOM.$purchasedOrder.data('total-revenue'), 10),
    };
    const orderPositions = DOM.$purchasedOrder.data('positions')
      .map(val => val.fields);

    yaTracker.purchase(orderPositions, orderData);
    gaTracker.purchase(orderPositions, orderData);
  }

  function reachGoal(goal) {
    /**
     * AdBlock-like services can block an yaCounter, so to prevent
     * interrupting of user session put reachGoal to try/catch.
     */
    try {
      yaCounter20644114.reachGoal(goal);
    } catch (e) {
      Sentry.captureException(e);  // Ignore ESLintBear (no-undef)
      console.error('YaCounter did not loaded. Perhaps the reason for this ' +
        `maybe AdBlock. Traceback: ${e}`);
    }
  }

  init();
})();
