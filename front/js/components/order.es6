(() => {
  const DOM = {
    $fancybox: $('.fancybox'),
    $formErrorText: $('.js-form-error-text'),
    $order: $('.js-order-contain'),
    $yandexFormWrapper: $('#yandex-form-wrapper'),
    yandexForm: '#yandex-form',
    submit: '#btn-send-se',
    fullForm: '#order-form-full',
    productCount: '.js-prod-count',
    remove: '.js-remove',
    paymentOptions: 'input[name=payment_type]',
    defaultPaymentOptions: 'input[for=id_payment_type_0]',
    orderForm: {
      name: '#id_name',
      phone: '#id_phone',
      email: '#id_email',
      city: '#id_city',
    },
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
    mediator.subscribe('onCartUpdate', renderTable, fillSavedInputs,
      touchSpinReinit, restoreSelectedPayment, cityAutocomplete);
    $(DOM.fullForm).submit(() => mediator.publish('onOrderSend'));

    /**
     * Bind events to parent's elements, because we can't bind event to dynamically added element.
     */
    DOM.$order.on('click', DOM.submit, submitOrder);
    DOM.$order.on('click', DOM.remove, () => removeProduct(getElAttr(event, 'productId')));
    DOM.$order.on('change', DOM.productCount, event => changeProductCount(event));
    DOM.$order.on('keyup', 'input', event => storeInput($(event.target)));
  }

  /**
   * Return element's attribute value by value name.
   */
  const getElAttr = (event, attributeName) => event.target.getAttribute(attributeName);

  /**
   * Init google cities autocomplete.
   */
  function cityAutocomplete() {
    const cityField = document.getElementById('id_city');
    if (!cityField) return;

    const autocompleteItem = new google.maps.places.Autocomplete(cityField, config.autocomplete);

    google.maps.event.addListener(autocompleteItem, 'place_changed', () => {
      storeInput($(DOM.orderForm.city));
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

    for (const fieldName in DOM.orderForm) {
      if ({}.hasOwnProperty.call(DOM.orderForm, fieldName)) {
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
   * Remove product from cart's table
   */
  const removeProduct = productId => {
    server.removeFromCart(productId)
      .then(data => {
        mediator.publish('onCartUpdate', data);
    });
  };

  /**
   * Event handler for changing product's count in Cart.
   * We wait at least 100ms every time the user pressed the button.
   */
  const changeProductCount = event => {
    const productID = getElAttr(event, 'productId');
    const newCount = event.target.value;

    setTimeout(
      () => server.changeInCart(productID, newCount)
        .then(data => mediator.publish('onCartUpdate', data)), 100
    );
  };

  /**
   * Return name (which is value) of a selected payment option.
   */
  const getSelectedPaymentName = () => $(`${DOM.paymentOptions}:checked`).val();

  /**
   * Return hash with customer's info from form.
   */
  const getOrderInfo = () => {
    const orderInfo = {
      payment_type: getSelectedPaymentName(),
    };

    $.each(DOM.orderForm, (name, field) => {
      orderInfo[name] = $(field).val();
    });

    return orderInfo;
  };

  function isValid(customerInfo) {
    return helpers.isPhoneValid(customerInfo.phone) && helpers.isEmailValid(customerInfo.email);
  }

  const isYandex = () => !config.sePayments.includes(getSelectedPaymentName());

  const renderYandexForm = formData => {
    const formHtml = `<form action="${formData['yandex_kassa_link']}" method="POST" id="yandex-form">
      <input type="text" name="shopId" value="${formData['shopId']}">
      <input type="text" name="scid" value="${formData['scid']}">
      <input type="text" name="shopSuccessURL" value="${formData['shopSuccessURL']}">
      <input type="text" name="shopFailURL" value="${formData['shopFailURL']}">
      <input type="text" name="cps_phone" value="${formData['cps_phone']}">
      <input type="text" name="cps_email" value="${formData['cps_email']}">
      <input type="text" name="sum" value="${formData['sum']}">
      <input type="text" name="customerNumber" value="${formData['customerNumber']}">
      <input type="text" name="orderNumber" value="${formData['orderNumber']}">
      <input type="text" name="paymentType" value="${formData['paymentType']}">
      <input type="submit">
    </form>`;

    DOM.$yandexFormWrapper.html(formHtml);
  };
  /**
   * Before submit: 
   * 1. Validate user's email and phone
   * 2. Define payment type, if it is Yandex order make request and wait response with form
   * 3. Submit this form.
   */
  const submitOrder = event => {
    const orderInfo = getOrderInfo();

    if (!isValid(orderInfo)) {
      DOM.$formErrorText.removeClass('hidden').addClass('shake animated');
      return;
    }

    if (isYandex()) {
      event.preventDefault();

      server.sendYandexOrder(orderInfo)
        .then(formData => {
          renderYandexForm(formData);
          $(DOM.yandexForm).submit();
        });
    }
  };

  /**
   * Store inputted value into LocalStorage.
   */
  const storeInput = target => {
    localStorage.setItem(target.attr('name'), target.val());
  };


  /**
   * Render table and form.
   * After that, fill in saved form data.
   */
  const renderTable = (event, data) => DOM.$order.html(data.table);

  init();
})();
