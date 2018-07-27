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

  const config = {
    phoneRegexp: /\d{3}-\d{2}-\d{2}/g,
    fullEmail: 'info@shopelectro.ru',
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
  const orderData = { id: 'DummyId' };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onOneClickBuy', (_, id, quantity, name) => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FAST_BUY_SEND');
      const productsData = {id, quantity, name};
      yaTracker.purchase(productsData, orderData);
      gaTracker.purchase(productsData, orderData);
    });
    mediator.subscribe('onOrderSend', (_, products) => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FULL_BUY_SEND');
      // Use a dummy order's id, because we do not wait complete processing of
      // purchase request.
      yaTracker.purchase(products, orderData);
      gaTracker.purchase(products, orderData);
    });
    // We receive an onProductAdd event from a category and a product pages
    mediator.subscribe('onProductAdd', (_, id, quantity) => {
      yaTracker.add([{ id, quantity }]);
    });
    mediator.subscribe('onProductRemove', (_, id, quantity) => {
      reachGoal('DELETE_PRODUCT');
      yaTracker.remove([{ id, quantity }]);
    });
    mediator.subscribe('onCartClear', (_, products) => {
      yaTracker.remove(products);
    });
    mediator.subscribe('onProductDetail', (_, id) => yaTracker.detail([{ id }]));
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
    DOM.$copyPhoneTag.mouseup(reachCopyPhone);
    DOM.$copyEmailTag.mouseup(reachCopyEmail);
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

  /**
   * Returns copied text by user.
   * http://stackoverflow.com/questions/5379120/get-the-highlighted-selected-text
   */
  const getSelectionText = () => window.getSelection().toString();

  /**
   * Fire when user selects 9 or more numbers of phone.
   */
  function reachCopyPhone() {
    const selectedTextLength = getSelectionText().length;

    if (selectedTextLength > 8) {
      localStorage.setItem('phoneIsCopied', 'true');
      reachGoal('COPY_PHONE');
    }
  }

  /**
   * We store this users event for current user.
   * So it fires once per user.
   */
  const isFullMailCopied = () => getSelectionText().indexOf(config.fullEmail) === 0;

  function reachCopyEmail() {
    const wasEmailCopied = localStorage.getItem('mailIsCopied');

    if (isFullMailCopied && !wasEmailCopied) {
      localStorage.setItem('mailIsCopied', 'true');
      reachGoal('COPY_MAIL');
    }
  }

  init();
})();
