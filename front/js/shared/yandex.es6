/**
 * Yandex module with Metrika.
 */
const yandex = (() => {
  const DOM = {
    $copyPhoneTag: $('.js-copy-phone'),
    $copyEmailTag: $('.js-copy-mail'),
    $backcallModal: $('.js-backcall-order'),
    $searchForm: $('.js-search-form'),
    $btnToCartProductPage: $('.js-to-cart-on-product-page'),
    $btnToCartCategoryPage: $('.js-product-to-cart'),
    $goToCartLink: $('.js-go-to-cart'),
    $removeFromCart: $('.js-remove'),
    $goToProductLink: $('.js-browse-product'),
    $downloadPrice: $('.js-download-price'),
    $downloadPriceInFooter: $('.js-download-price-footer'),
  };

  const CONFIG = {
    phoneRegexp: /\d{3}-\d{2}-\d{2}/g,
    fullEmail: 'info@shopelectro.ru',
  };

  const init = () => {
    setUpListeners();
  };

  const setUpListeners = () => {
    mediator.subscribe('onOneClickBuy', () => reachGoal('ONE_CLICK_BUY_SEND'));
    mediator.subscribe('onProductRemove', () => reachGoal('DELETE_PRODUCT'));
    mediator.subscribe('onOrderSend', () => reachGoal('FULL_BUY_SEND'));
    mediator.subscribe('onBackCallSend', reachGoal('BACK_CALL_SEND'));
    DOM.$searchForm.submit(() => reachGoal('USE_SEARCH_FORM'));
    DOM.$removeFromCart.click(() => reachGoal('DELETE_PRODUCT'));
    DOM.$goToCartLink.click(() => reachGoal('CART_OPEN'));
    DOM.$backcallModal.click(() => reachGoal('BACK_CALL_OPEN'));
    DOM.$goToProductLink.click(() => reachGoal('PROD_BROWSE'));
    DOM.$downloadPrice.click(() => reachGoal('PRICE_HEADER'));
    DOM.$downloadPriceInFooter.click(() => reachGoal('PRICE_FOOTER'));
    DOM.$btnToCartProductPage
      .click(() => reachGoal('PUT_IN_CART_FROM_PRODUCT'))
      .click(() => reachGoal('CMN_PUT_IN_CART'));
    DOM.$btnToCartCategoryPage
      .click(() => reachGoal('PUT_IN_CART_FROM_CATEGORY'))
      .click(() => reachGoal('CMN_PUT_IN_CART'));
    DOM.$copyPhoneTag.mouseup(reachCopyPhone);
    DOM.$copyEmailTag.mouseup(reachCopyEmail);
  };

  const reachGoal = (goal) => {
    yaCounter.reachGoal(goal);
  };

  /**
   * We store this users event for current user.
   * So it fires once per user.
   */
  const reachCopyPhone = () => {
    const wasPhoneCopied = localStorage.getItem('phoneIsCopied');
    const isFullPhoneNumberCopied = validator.isPhoneValid(getSelectionText());

    if (isFullPhoneNumberCopied && !wasPhoneCopied) {
      localStorage.setItem('phoneIsCopied', 'true');
      reachGoal('COPY_PHONE');
    }
  };

  /**
   * We store this users event for current user.
   * So it fires once per user.
   */
  const reachCopyEmail = () => {
    const wasEmailCopied = localStorage.getItem('mailIsCopied');

    if (isFullMailCopied && !wasEmailCopied) {
      localStorage.setItem('mailIsCopied', 'true');
      reachGoal('COPY_MAIL');
    }
  };

  const isFullMailCopied = () => getSelectionText().indexOf(CONFIG.fullEmail) === 0;

  /**
   * Returns copied text by user.
   * http://stackoverflow.com/questions/5379120/get-the-highlighted-selected-text
   */
  const getSelectionText = () => window.getSelection().toString();

  init();
})();
