(() => {
  const DOM = {
    $fancybox: $('.fancybox'),
    $formErrorText: $('.js-form-error-text'),
    $order: $('.js-order-contain'),
    yandexFormWrapper: '#yandex-form-wrapper',
    yandexForm: '#yandex-form',
    productRows: '.div-table-row',
    submit: '#submit-order',
    fullForm: '#order-form-full',
    productCount: '.js-prod-count',
    remove: '.js-remove',
    paymentOptions: 'input[name=payment_type]',
    defaultPaymentOptions: 'input[for=id_payment_type_0]',
    orderFieldData: $('#order-form-full').data('fields'),
  };

  const config = {
    autocomplete: {
      types: ['(cities)'],
      componentRestrictions: {
        country: 'ru',
      },
    },
    sePayments: ['cash', 'cashless'],
    paymentKey: 'payment',
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
    fillSavedInputs();
    restoreSelectedPayment();
  };

  function pluginsInit() {
    cityAutocomplete();
  }

  function setUpListeners() {
    mediator.subscribe(
      'onCartUpdate', renderTable, fillSavedInputs,
      touchSpinReinit, restoreSelectedPayment, cityAutocomplete,
    );

    /**
     * Bind events to parent's elements, because of dynamic elements.
     */
    DOM.$order.on('click', DOM.submit, submitOrder);
    DOM.$order.on('click', DOM.remove, removeProduct);
    DOM.$order.on('change', DOM.productCount, helpers.debounce(changeProductCount, 250));
    DOM.$order.on('keyup', 'input', event => storeInput($(event.target)));
  }

  /**
   * Init google cities autocomplete.
   */
  function cityAutocomplete() {
    const cityField = document.getElementById('id_city');
    if (!cityField) return;

    const autocompleteItem = new google.maps.places.Autocomplete(cityField, config.autocomplete);

    google.maps.event.addListener(autocompleteItem, 'place_changed', () => {
      storeInput($(DOM.orderFieldData.city));
    });
  }

  /**
   * Reinit touchspin plugin cause of dynamic DOM.
   */
  function touchSpinReinit() {
    $(DOM.productCount).TouchSpin(configs.plugins.touchspin);
  }

  /**
   * Fill inputs, which have saved to localstorage value.
   * Runs on page load, and on every cart's update.
   */
  function fillSavedInputs() {
    const getFieldByName = name => $(`#id_${name}`);

    for (const fieldName in DOM.orderFieldData) {  // Ignore ESLintBear (no-restricted-syntax)
      if ({}.hasOwnProperty.call(DOM.orderFieldData, fieldName)) {
        const $field = getFieldByName(fieldName);
        const savedValue = localStorage.getItem(fieldName);

        if ($field && savedValue) {
          $field.val(savedValue);
        }
      }
    }
  }

  /**
   * Select saved payment if there is one.
   */
  function restoreSelectedPayment() {
    const savedPayment = localStorage.getItem(config.paymentKey);

    if (savedPayment) {
      const isSelected = $option => $option.val() === savedPayment;

      $(DOM.paymentOptions).each((_, el) => {
        $(el).attr('checked', isSelected($(el)));
      });
    } else {
      $(DOM.defaultPaymentOptions).attr('checked', true);
    }
  }

  /**
   * Remove Product from Cart.
   */
  function removeProduct(event) {
    const $target = $(event.currentTarget);
    const id = $target.data('product-id');
    const quantity = $target.data('product-count');
    server.removeFromCart(id)
      .then((data) => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onProductRemove', [{ id, quantity }]);
      });
  }


  /**
   * Handle Product's count change in Cart with delay.
   */
  function changeProductCount(event) {
    const $target = $(event.currentTarget);
    const id = $target.data('product-id');
    const countDiff = event.target.value - $target.data('last-count');
    const data = {
      id,
      quantity: Math.abs(countDiff),
    };

    server.changeInCart(id, event.target.value)
      .then((newData) => {
        mediator.publish('onCartUpdate', newData);
        mediator.publish(countDiff > 0 ? 'onProductAdd' : 'onProductRemove', [data]);
      });
  }


  /**
   * Return name (which is value) of a selected payment option.
   */
  const getSelectedPayment = () => $(`${DOM.paymentOptions}:checked`).val();

  /**
   * Return hash with customer's info from form.
   */
  const getOrderInfo = () => {
    const orderInfo = Object.keys(DOM.orderFieldData).reduce((acc, key) => {
      acc[key] = $(DOM.orderFieldData[key]).val();
      return acc;
    }, {});
    orderInfo.payment_type = getSelectedPayment();
    return orderInfo;
  };

  /**
   * Return true if form has valid phone & email.
   */
  function isValid(customerInfo) {
    return helpers.isPhoneValid(customerInfo.phone) &&
           helpers.isEmailValid(customerInfo.email);
  }

  function renderYandexForm(formData) {
    const formHtml = `
      <form action="${formData.yandex_kassa_link}" method="POST" id="yandex-form">
        <input type="text" name="shopId" value="${formData.shopId}">
        <input type="text" name="scid" value="${formData.scid}">
        <input type="text" name="shopSuccessURL" value="${formData.shopSuccessURL}">
        <input type="text" name="shopFailURL" value="${formData.shopFailURL}">
        <input type="text" name="cps_phone" value="${formData.cps_phone}">
        <input type="text" name="cps_email" value="${formData.cps_email}">
        <input type="text" name="sum" value="${formData.sum}">
        <input type="text" name="customerNumber" value="${formData.customerNumber}">
        <input type="text" name="orderNumber" value="${formData.orderNumber}">
        <input type="text" name="paymentType" value="${formData.paymentType}">
      </form>
    `;
    // use non-cached version of ya wrapper, because it may be updated
    $(DOM.yandexFormWrapper).append($(formHtml));
  }

  /**
   * Before submit:
   * 1. Validate user's email and phone.
   * 2. Define payment type, if it is Yandex order make request and wait response with form.
   * 3. Submit this form.
   */
  function submitOrder(event) {
    event.preventDefault();
    const orderInfo = getOrderInfo();

    if (!isValid(orderInfo)) {
      DOM.$formErrorText.removeClass('hidden').addClass('shake animated');
      return;
    }

    // disable button to prevent user's multiple clicks;
    helpers.setDisabledState($(DOM.submit));

    // setTimeout to wait "onOrderSend" handling
    const submit = selector => setTimeout(() => $(selector).submit(), 100);
    const isYandex = () => !config.sePayments.includes(getSelectedPayment());

    // onOrderSend must be triggered before submit
    mediator.publish('onOrderSend');

    if (isYandex()) {
      // @todo #473:30m Test order redirect to ya.kassa
      server.sendYandexOrder(orderInfo)
        .then(formData => renderYandexForm(formData))
        .then(() => submit(DOM.yandexForm));
    } else {
      submit(DOM.fullForm);
    }
  }

  /**
   * Store inputted value into LocalStorage.
   */
  function storeInput(target) {
    localStorage.setItem(target.attr('name'), target.val());
  }

  /**
   * Render table and form.
   * Fill in saved form data after.
   */
  function renderTable(_, data) {
    DOM.$order.html(data.table);
  }

  init();
})();
