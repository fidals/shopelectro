(() => {
  const DOM = {
    $fancybox: $('.fancybox'),
    $formErrorText: $('.js-form-error-text'),
    $order: $('.js-order-contain'),
    $yandexFormWrapper: $('#yandex-form-wrapper'),
    yandexForm: '#yandex-form',
    productRows: '.div-table-row',
    submit: '#submit-order',
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
    mediator.subscribe(
      'onCartUpdate', renderTable, fillSavedInputs,
      touchSpinReinit, restoreSelectedPayment, cityAutocomplete,
    );
    $(DOM.fullForm).submit(() => mediator.publish('onOrderSend', [getProductsData()]));

    /**
     * Bind events to parent's elements, because of dynamic elements.
     */
    DOM.$order.on('click', DOM.submit, submitOrder);
    DOM.$order.on('click', DOM.remove, event => removeProduct(
      getElAttr(event, 'productId'), getElAttr(event, 'productCount'),
    ));
    DOM.$order.on('change', DOM.productCount, helpers.debounce(changeProductCount, 250));
    DOM.$order.on('keyup', 'input', event => storeInput($(event.target)));
  }

  function getProductsData() {
    return $(DOM.productRows).map((_, el) => {
      let $el = $(el);
      return {
        id: $el.attr('data-table-id'),
        name: $el.find('.js-product-link').text(),
        quantity: $el.find('.js-prod-count').val(),
      }
    }).get()
  }

  /**
   * Return element's attribute value by attr name.
   */
  function getElAttr(event, attrName) {
    return event.currentTarget.getAttribute(attrName);
  }

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

    for (const fieldName in DOM.orderForm) {  // Ignore ESLintBear (no-restricted-syntax)
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
   * Remove Product from Cart.
   */
  function removeProduct(productId, count) {
    server.removeFromCart(productId)
      .then((data) => {
        mediator.publish('onCartUpdate', data);
        mediator.publish('onProductRemove', [productId, count]);
      });
  }

  /**
   * Handle Product's count change in Cart with delay.
   */
  function changeProductCount(event) {
    const productID = getElAttr(event, 'productId');
    server.changeInCart(productID, event.target.value)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  /**
   * Return name (which is value) of a selected payment option.
   */
  const getSelectedPayment = () => $(`${DOM.paymentOptions}:checked`).val();

  /**
   * Return hash with customer's info from form.
   */
  const getOrderInfo = () => {
    const orderInfo = {
      payment_type: getSelectedPayment(),
    };

    $.each(DOM.orderForm, (name, field) => {
      orderInfo[name] = $(field).val();
    });

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
        <input type="submit">
      </form>
    `;

    DOM.$yandexFormWrapper.html(formHtml);
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

    helpers.setDisabledState($(DOM.submit)); // disable button to prevent user's multiple clicks;

    const isYandex = () => !config.sePayments.includes(getSelectedPayment());
    if (isYandex()) {
      server.sendYandexOrder(orderInfo)
        .then((formData) => {
          renderYandexForm(formData);
          $(DOM.yandexForm).submit();
        });
    } else {
      $(DOM.fullForm).submit();
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
  function renderTable(event, data) {
    DOM.$order.html(data.table);
  }

  init();
})();
