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
  };

  // Sync container for yaTracker
  window.dataLayer = window.dataLayer || [];
  // Load ecommerce plugin for gaTracker
  try {
    ga('require', 'ecommerce');  // Ignore ESLintBear (block-scoped-var)
  } catch (e) {
    var ga = console.error;  // Ignore ESLintBear (no-var)
    console.error(`GaTracker failed to load. Traceback: ${e}`);
  }

  const yaTracker = new YATracker(window.dataLayer, 'RUB');  // Ignore ESLintBear (no-undef)
  const gaTracker = new GATracker(ga, 'ecommerce');  // Ignore ESLintBear (block-scoped-var)

  // @todo #504:60m Send `purchase` event to YA and GA after a success purchase.
  //  This will allow us to send order's id. Currently we send the event after
  //  submitting of the purchase button with the dummy order's id.
  //  See the parent issue for a detail.

  // Use a dummy order's id, because we do not wait complete processing of
  // purchase request.
  const orderData = { id: 1 };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onOneClickBuy', (_, productsData) => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FAST_BUY_SEND');
      yaTracker.purchase([productsData], orderData);
      gaTracker.purchase([productsData], orderData);
    });
    mediator.subscribe('onOrderSend', (_, products) => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FULL_BUY_SEND');
      yaTracker.purchase(products, orderData);
      gaTracker.purchase(products, orderData);
    });
    mediator.subscribe('onCartClear', (_, products) => {
      yaTracker.remove(products);
    });
    // We receive an onProductAdd event from a category and a product pages
    mediator.subscribe('onProductAdd', (_, data) => {
      yaTracker.add([data]);
    });
    mediator.subscribe('onProductRemove', (_, id, quantity) => {
      reachGoal('DELETE_PRODUCT');
      yaTracker.remove([{ id, quantity }]);
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

  function reachGoal(goal) {
    /**
     * AdBlock-like services can block an yaCounter, so to prevent
     * interrupting of user session put reachGoal to try/catch.
     */
    try {
      yaCounter20644114.reachGoal(goal);
    } catch (e) {
      console.error('YaCounter did not loaded. Perhaps the reason for this ' +
        `maybe AdBlock. Traceback: ${e}`);
    }
  }

  init();
})();
