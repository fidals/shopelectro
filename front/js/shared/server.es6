/**
 * Sends information about order call.
 * @param phone
 * @param time
 * @param url
 */
const sendOrderCall = (phone, time, url) => {
  return $.post(
    '/shop/order-call/',
    {
      phone: phone,
      time: time,
      url: url
    }
  );
};

const fetchProducts = (url) => fetch(url).then((response) => response.text());

const sendViewType = (event, viewType) => {
  $.post('/set-view-type/', {view_type: viewType});
};

/**
 * Add product to backend's Cart.
 * @param productId
 * @param quantity
 */
const addToCart = (productId, quantity) => {
  return $.post(
    '/shop/cart-add/',
    {
      quantity: quantity,
      product: productId
    }
  );
};

/**
 * Flush (or clear) the cart on backend.
 */
const flushCart = () => $.post('/shop/cart-flush/');

/**
 * Handle one-click-buy feature. Sends:
 * @param productId - id of a bought product
 * @param quantity - selected quantity
 * @param phone - customer's phone
 */
const oneClickBuy = (productId, quantity, phone) => {
  return $.post(
    '/shop/one-click-buy/',
    {
      product: productId,
      quantity: quantity,
      phone: phone
    }
  );
};

/**
 * Remove given product from cart.
 * @param productId
 */
const removeFromCart = (productId) => {
  return $.post(
    '/shop/cart-remove/',
    {
      product: productId
    }
  );
};

/**
 * Return $.post request, which changes quantity of a given product in Cart.
 * @param productId
 * @param quantity - new quantity of a product
 */
const changeInCart = (productId, quantity) => {
  return $.post(
    '/shop/cart-change/',
    {
      product: productId,
      quantity: quantity
    }
  );
};

const sendYandexOrder = (data) => {
  return $.post(
    '/shop/yandex-order/',
    data
  );
};
