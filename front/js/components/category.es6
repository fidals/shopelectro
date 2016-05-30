/**
 * Category Page module defines logic, operations and DOM for CategoryPage.
 */
const categoryModule = (function () {
  const DOM = {
    loadedProducts: $('.js-products-showed-count'),
    productsList: $('#products-wrapper'),
    viewType: $('#category-right'),
    loadMore: $('#btn-load-products'),
    tileView: {
      $: $('.js-icon-mode-tile'),
      mode: 'tile',
    },
    listView: {
      $: $('.js-icon-mode-list'),
      mode: 'list',
    },
    sorting: $('.selectpicker'),
  };

  const CONFIG = {
    productsToFetch: 30,
    totalProductsCount: parseInt($('.js-total-products').first().text()),
  };

  let init = () => {
    setUpListeners();
    updateButtonState();
  };

  /**
   * Subscribing on events using mediator.
   */
  let setUpListeners = () => {
    DOM.loadMore.click(loadProducts);
    DOM.sorting.change(changeSort);
    DOM.tileView.$.click(() => mediator.publish('onViewTypeChange', DOM.tileView.mode));
    DOM.listView.$.click(() => mediator.publish('onViewTypeChange', DOM.listView.mode));
    mediator.subscribe('onViewTypeChange', updateViewType, sendViewType);
    mediator.subscribe('onProductsLoad', updateLoadedCount, updateProductsList, updateButtonState);
  };

  /**
   * Changes sorting option and re-renders the whole screen.
   */
  let changeSort = () => location.href = sortingOption().attr('data-path');

  /**
   * Updates Products List DOM via appending html-list of loaded products
   * to wrapper.
   *
   * @param {Event} event
   * @param {string} products - HTML string of fetched product's list
   */
  let updateProductsList = (event, products) => DOM.productsList.append(products);

  /**
   * Updates loaded products counter by a simple logic:
   * 1) if we have less products left than we can fetch at a time, it means we have loaded them all,
   *    so we should set loaded count a value of total products
   * 2) otherwise, we simply add PRODUCTS_TO_FETCH to counter.
   */
  let updateLoadedCount = () =>
    DOM.loadedProducts.text(loadedProductsCount() + Math.min(productsLeft(), CONFIG.productsToFetch));

  /**
   * Adds 'hidden' class to button if there are no more products to load.
   */
  let updateButtonState = () => {
    if (productsLeft() === 0) {
      DOM.loadMore.addClass('hidden');
    }
  };

  /**
   * Updates view of a product's list.
   *
   * Removes old classes and adds new one depends on what view type was selected.
   * @param {Event} event
   * @param {string} viewType: list|tile
   */
  let updateViewType = (event, viewType) => {
    DOM.viewType
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
  let sortingOption = () => DOM.sorting.find(':selected');

  /**
   * Number of products remained un-fetched from back-end.
   * Calculates due to a simple formula:
   *  left products = total products - already loaded products
   *
   * @returns {Number} - number of products left to fetch
   */
  let productsLeft = () => parseInt(CONFIG.totalProductsCount - loadedProductsCount());

  /**
   * Gets number of already loaded products
   *
   * @returns {int} - number of products which are loaded and presented in DOM
   */
  let loadedProductsCount = () => parseInt(DOM.loadedProducts.first().text());

  /**
   * Loads products from back-end using promise-like fetch object fetchProducts.
   * After products successfully loaded - publishes 'onProductLoad' event.
   */
  let loadProducts = () => {
    let categoryUrl = DOM.loadMore.attr('data-url');
    let offset = loadedProductsCount();
    let sorting = sortingOption().val();
    let url = `${categoryUrl}load-more/${offset}/${sorting}`;

    fetchProducts(url)
      .then((products) => mediator.publish('onProductsLoad', products));
  };

  init();
}());
