(() => {
  const DOM = {
    $purchasedOrder: $('.js-purchased-order'),
  };

  const init = () => {
    publishSuccessOrder();
  };

  function publishSuccessOrder() {
    const isSuccessPage = window.location.href.includes('order-success');
    const hasData = DOM.$purchasedOrder.length;

    if (!isSuccessPage) {
      return;
    } else if (!hasData) {
      console.error('Success page doesn\'t contain purchased order data.');
      return;
    }

    const orderData = {
      id: DOM.$purchasedOrder.data('id'),
      revenue: parseFloat(DOM.$purchasedOrder.data('total-revenue'), 10),
    };
    const orderPositions = DOM.$purchasedOrder.data('positions')
      .map(val => val.fields);

    mediator.publish('onSuccessOrder', [orderPositions, orderData]);
  }

  init();
})();
