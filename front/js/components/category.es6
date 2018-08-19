(() => {
  const DOM = {
    $h1: $('.category-title'),
    $productsOnPage: $('.js-products-showed-count'),
    $productsList: $('#products-wrapper'),
    $viewType: $('#category-right'),
    $loadMoreBtn: $('#btn-load-products'),
    addToCart: '.js-product-to-cart',
    totalProducts: '.js-total-products',
    tileView: {
      $: $('.js-icon-mode-tile'),
      mode: 'tile',
    },
    listView: {
      $: $('.js-icon-mode-list'),
      mode: 'list',
    },
    $sorting: $('.selectpicker'),
    $pagination: $('.js-catalog-pagination'),
  };

  const init = () => {
    setUpListeners();
    updateLoadMoreBtnState();
    hidePaginationButtons();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    mediator.subscribe('onViewTypeChange', updateViewType, server.sendViewType);
    mediator.subscribe(
      'onProductsLoad',
      updateProductsList,
      updateLoadedCount,
      updateLoadMoreBtnState,
      configs.initTouchspin,
    );
    DOM.tileView.$.click(() => mediator.publish('onViewTypeChange', DOM.tileView.mode));
    DOM.listView.$.click(() => mediator.publish('onViewTypeChange', DOM.listView.mode));

    DOM.$loadMoreBtn.click(loadProducts);
    DOM.$sorting.change(reloadPageWithSorting);
    $(document).on('click', DOM.addToCart, buyProduct);
  }

  const getSelectedSortingOption = () => DOM.$sorting.find(':selected');

  /**
   * Get number of already loaded products
   *
   * @returns {int} - number of products which are presented in DOM
   */
  const getProductsOnPageCount = () => parseInt(DOM.$productsOnPage.first().text(), 10);

  /**
   * Hide catalog's pagination buttons.
   * Buttons should be visible only for web search engines.
   */
  function hidePaginationButtons() {
    DOM.$pagination.hide();
  }

  /**
   * Get number of already loaded products
   *
   * @param {string} products
   * @returns {number}
   */
  function getLoadedProductsCount(products) {
    return (products.match(new RegExp('js-product-to-cart', 'g')) || []).length;
  }

  /**
   * Number of Products remain un-loaded from server.
   * Formula:
   * productsLeft = total products on server - already loaded products on front
   *
   * @returns {Number} - number of products left to load
   */
  function productsLeft() {
    const totalProductsCount = parseInt($(DOM.totalProducts).first().text(), 10);
    return totalProductsCount - getProductsOnPageCount();
  }

  function reloadPageWithSorting() {
    const tags = helpers.getUrlEndpointParam('tags');
    const selectedSorting = getSelectedSortingOption().attr('data-path').trim();
    if (tags === '') {
      window.location.href = selectedSorting;
    } else {
      window.location.href = `${selectedSorting}tags/${tags}/`;
    }
  }

  /**
   * Append loaded Products from server in DOM.
   *
   * @param {string} products
   */
  function updateProductsList(_, products) {
    DOM.$productsList.append(products);
  }

  /**
   * Update loaded Products counter.
   */
  function updateLoadedCount(_, products) {
    // Aggregate `js-products-showed-count` by `getLoadedProductsCount()`.
    DOM.$productsOnPage.text(getProductsOnPageCount() + getLoadedProductsCount(products));
  }

  /**
   * Add 'hidden' class to button if there are no more Products to load.
   */
  function updateLoadMoreBtnState() {
    if (productsLeft() !== 0) return;
    DOM.$loadMoreBtn.addClass('hidden');
  }

  /**
   * Update Product list view.
   * Toggles classes depends on what view type was selected.
   * @param {string} viewType: list|tile
   */
  function updateViewType(_, viewType) {
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
  }

  /**
   * Load Products from server.
   * Publish 'onProductLoad' event on success.
   */
  function loadProducts() {
    const path = DOM.$loadMoreBtn.data('url');
    const offset = getProductsOnPageCount();
    const sorting = getSelectedSortingOption().val();
    const filterParams = helpers.getUrlEndpointParam('tags');
    let url = `${path}load-more/${offset}/${sorting}/`;

    if (filterParams) url += `tags/${filterParams}/`;
    server.loadProducts(url)
      .then(products => mediator.publish('onProductsLoad', products));
  }

  /**
   * Send Product's id and quantity on server.
   * Publish 'onCartUpdate' event on success.
   */
  function buyProduct(event) {
    const getProductData = () => {
      const $product = $(event.target);
      const quantity = $product.closest('.js-order').find('.js-product-count').val();

      return {
        id: parseInt($product.attr('productId'), 10),
        name: $product.attr('productName'),
        quantity: parseInt(quantity, 10),
        category: DOM.$h1.data('name'),
        brand: $product.attr('productBrand'),
      };
    };

    const data = getProductData();
    const { id, quantity } = data;

    server.addToCart(id, quantity)
      .then((newData) => {
        mediator.publish('onCartUpdate', newData);
        mediator.publish('onProductAdd', [data]);
      });
  }

  init();
})();
