(() => {
  const DOM = {
    $purchasedOrder: $('.js-purchased-order'),
  };

  const init = () => {
  	publishSuccessOrder();
  };

  function publishSuccessOrder() {
    if (!DOM.$purchasedOrder.length) {
    	if (window.location.href.includes('order-success')) {
	      console.error('Success page doesn\'t contain purchased order data.');
    	}
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
