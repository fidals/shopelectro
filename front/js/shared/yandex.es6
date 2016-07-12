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
    DOM.$searchForm.submit(reachSearch);
    DOM.$copyPhoneTag.mouseup(copyPhone);
    DOM.$copyEmailTag.mouseup(copyEmail);
    DOM.$removeFromCart.click(reachRemoveFromCart);
    DOM.$goToCartLink.click(reachCartOpen);
    DOM.$backcallModal.click(reachBackCallOpen);
    DOM.$goToProductLink.click(reachProductBrowse);
    DOM.$downloadPrice.click(reachDownloadPrice);
    DOM.$downloadPriceInFooter.click(reachDownloadPriceInFooter);
    DOM.$btnToCartProductPage
      .click(reachToCartOnProductPage)
      .click(reachCommonPutInCart);
    DOM.$btnToCartCategoryPage
      .click(reachToCartOnCategoryPage)
      .click(reachCommonPutInCart);
  };

  const reachBackCallOpen = () => {
    yaCounter20644114.reachGoal('BACK_CALL_OPEN');
  };

  const reachCartOpen = () => {
    yaCounter20644114.reachGoal('CART_OPEN');
  };

  const reachProductBrowse = () => {
    yaCounter20644114.reachGoal('PROD_BROWSE');
  };

  const reachSearch = () => {
    yaCounter20644114.reachGoal('USE_SEARCH_FORM');
  };

  const reachToCartOnProductPage = () => {
    yaCounter20644114.reachGoal('PUT_IN_CART_FROM_PRODUCT');
  };

  const reachToCartOnCategoryPage = () => {
    yaCounter20644114.reachGoal('PUT_IN_CART_FROM_CATEGORY');
  };

  const reachCommonPutInCart = () => {
    yaCounter20644114.reachGoal('CMN_PUT_IN_CART');
  };

  const reachRemoveFromCart = () => {
    yaCounter20644114.reachGoal('DELETE_PRODUCT');
  };

  const reachDownloadPrice = () => {
    yaCounter20644114.reachGoal('PRICE_HEADER');
  };

  const reachDownloadPriceInFooter = () => {
    yaCounter20644114.reachGoal('PRICE_FOOTER');
  };

  /**
   * We store this users event for current user.
   * So it fires once per user.
   */
  const copyPhone = () => {
    const isTextMatched = getSelectionText().match(CONFIG.phoneRegexp);
    const wasPhoneCopied = localStorage.getItem('phoneIsCopied');

    if (!!isTextMatched && wasPhoneCopied !== 'true') {
      localStorage.setItem('phoneIsCopied', 'true');

      yaCounter20644114.reachGoal('COPY_PHONE');
    }
  };

  /**
   * We store this users event for current user.
   * So it fires once per user.
   */
  const copyEmail = () => {
    const textMatched = getSelectionText().indexOf(CONFIG.fullEmail);
    const wasEmailCopied = localStorage.getItem('mailIsCopied');

    if (textMatched === 0 && wasEmailCopied !== 'true') {
      localStorage.setItem('mailIsCopied', 'true');

      yaCounter20644114.reachGoal('COPY_MAIL');
    }
  };

  /**
   * Returns copied text by user.
   * http://stackoverflow.com/questions/5379120/get-the-highlighted-selected-text
   */
  const getSelectionText = () => window.getSelection().toString();

  init();
})();
