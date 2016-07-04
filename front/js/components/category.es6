/**
 * Category Page module defines logic, operations and DOM for CategoryPage.
 */
const category = (() => {
  const DOM = {
    $loadedProducts: $('.js-products-showed-count'),
    $productsList: $('#products-wrapper'),
    $viewType: $('#category-right'),
    $loadMore: $('#btn-load-products'),
    $addToCart: $('.js-product-to-cart'),
    tileView: {
      $: $('.js-icon-mode-tile'),
      mode: 'tile',
    },
    listView: {
      $: $('.js-icon-mode-list'),
      mode: 'list',
    },
    $sorting: $('.selectpicker'),
  };

  const CONFIG = {
    productsToFetch: 30,
    totalProductsCount: parseInt($('.js-total-products').first().text()),
  };

  const init = () => {
    setUpListeners();
    updateButtonState();
  };

  /**
   * Subscribing on events using mediator.
   */
  const setUpListeners = () => {
    DOM.$loadMore.click(loadProducts);
    DOM.$sorting.change(changeSort);
    DOM.tileView.$.click(() => mediator.publish('onViewTypeChange', DOM.tileView.mode));
    DOM.listView.$.click(() => mediator.publish('onViewTypeChange', DOM.listView.mode));
    DOM.$addToCart.click((event) => buyProduct(event));
    mediator.subscribe('onViewTypeChange', updateViewType, server.sendViewType);
    mediator.subscribe('onProductsLoad', updateLoadedCount, updateProductsList, updateButtonState);
  };

  /**
   * Changes sorting option and re-renders the whole screen.
   */
  const changeSort = () => {
    location.href = sortingOption().attr('data-path');
  };

  /**
   * Updates Products List DOM via appending html-list of loaded products
   * to wrapper.
   *
   * @param {Event} event
   * @param {string} products - HTML string of fetched product's list
   */
  const updateProductsList = (event, products) => DOM.$productsList.append(products);

  /**
   * Updates loaded products counter by a simple logic:
   * 1) if we have less products left than we can fetch at a time, it means we have loaded them all,
   *    so we should set loaded count a value of total products
   * 2) otherwise, we simply add PRODUCTS_TO_FETCH to counter.
   */
  const updateLoadedCount = () => DOM.$loadedProducts.text(
    loadedProductsCount() + Math.min(productsLeft(), CONFIG.productsToFetch)
  );

  /**
   * Adds 'hidden' class to button if there are no more products to load.
   */
  const updateButtonState = () => {
    if (productsLeft() === 0) {
      DOM.$loadMore.addClass('hidden');
    }
  };

  /**
   * Updates view of a product's list.
   *
   * Removes old classes and adds new one depends on what view type was selected.
   * @param {Event} event
   * @param {string} viewType: list|tile
   */
  const updateViewType = (event, viewType) => {
    DOM.$viewType
      .removeClass('view-mode-tile view-mode-list')
      .addClass(`view-mode-${viewType}`);

    if (viewType === DOM.listView.mode) {
      DOM.listView.$.addClass('active');
      DOM.tileView.$.removeClass('active');
    } else {
      DOM.tileView.$.addClass('active');
      DOM.listView.$.removeClass('active');
    }
  };

  /**
   * Returns selected sorting option.
   */
  const sortingOption = () => DOM.$sorting.find(':selected');

  /**
   * Number of products remained un-fetched from back-end.
   * Calculates due to a simple formula:
   * left products = total products - already loaded products
   *
   * @returns {Number} - number of products left to fetch
   */
  const productsLeft = () => parseInt(CONFIG.totalProductsCount - loadedProductsCount());

  /**
   * Gets number of already loaded products
   *
   * @returns {int} - number of products which are loaded and presented in DOM
   */
  const loadedProductsCount = () => parseInt(DOM.$loadedProducts.first().text());

  /**
   * Loads products from back-end using promise-like fetch object fetchProducts.
   * After products successfully loaded - publishes 'onProductLoad' event.
   */
  const loadProducts = () => {
    const categoryUrl = DOM.$loadMore.attr('data-url');
    const offset = loadedProductsCount();
    const sorting = sortingOption().val();
    const url = `${categoryUrl}load-more/${offset}/${sorting}`;

    server.fetchProducts(url)
      .then((products) => mediator.publish('onProductsLoad', products));
  };

  const buyProduct = (event) => {
    const buyInfo = () => {
      const product = $(event.target);
      const count = product.closest('.js-order').find('.js-product-count').val();
      return {
        count: parseInt(count),
        id: parseInt(product.attr('productId')),
      };
    };

    const { id, count } = buyInfo(event);
    server.addToCart(id, count).then((data) => mediator.publish('onCartUpdate', data));
  };

  init();
})();
