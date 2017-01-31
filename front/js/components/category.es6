{
  const DOM = {
    $productsOnPage: $('.js-products-showed-count'),
    $productsList: $('#products-wrapper'),
    $viewType: $('#category-right'),
    $loadMoreBtn: $('#btn-load-products'),
    addToCart: '.js-product-to-cart',
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

  const config = {
    productsToLoad: 48,
    totalProductsCount: parseInt($('.js-total-products').first().text(), 10),
  };

  const init = () => {
    setUpListeners();
    updateLoadMoreBtnState();
  };

  /**
   * Subscribing on events using mediator.
   */
  function setUpListeners() {
    mediator.subscribe('onViewTypeChange', updateViewType, server.sendViewType);
    mediator.subscribe('onProductsLoad', updateProductsList, updateLoadedCount,
      updateLoadMoreBtnState, configs.initTouchspin);
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
  const productsOnPage = () => parseInt(DOM.$productsOnPage.first().text(), 10);

  /**
   * Number of products remain un-loaded from server.
   * Formula:
   * productsLeft = total products on server - already loaded products on front
   *
   * @returns {Number} - number of products left to load
   */
  const productsLeft = () => parseInt(config.totalProductsCount - productsOnPage(), 10);

  const getFilterQueryParam = () => window.location.search.split('tags=')[1];

  function reloadPageWithSorting() {
    location.href = getSelectedSortingOption().attr('data-path');
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
   * Update loaded products counter by a simple logic:
   * 1) if we have less products left than we can load at a time, it means we have loaded them all,
   *    so we should set loaded count a value of total products
   * 2) otherwise, we simply add `config.productsToLoad` to counter.
   */
  function updateLoadedCount() {
    DOM.$productsOnPage.text(
      productsOnPage() + Math.min(productsLeft(), config.productsToLoad),
    );
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
    const offset = productsOnPage();
    const sorting = getSelectedSortingOption().val();
    const filterParams = getFilterQueryParam();
    let url = `${path}load-more/${offset}/${sorting}/`;

    if (filterParams) url += `?tags=${filterParams}`;
    server.loadProducts(url)
      .then(products => mediator.publish('onProductsLoad', products));
  }

  /**
   * Send Product's id and quantity on server.
   * Publish 'onCartUpdate' event on success.
   */
  function buyProduct(event) {
    const buyInfo = () => {
      const product = $(event.target);
      const count = product.closest('.js-order').find('.js-product-count').val();

      return {
        count: parseInt(count, 10),
        id: parseInt(product.attr('productId'), 10),
      };
    };

    const { id, count } = buyInfo();

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  init();
}
