const order = (() => {
  const DOM = {
    $fancybox: $('.fancybox'),
    $formErrorText: $('.js-form-error-text'),
    $order: $('.js-order-contain'),
    yandexSubmit: '#btn-send-ya',
    seSubmit: '#btn-send-se',
    yandexForm: '#yandex-form',
    productCount: '.js-prod-count',
    remove: '.js-remove',
    paymentOptions: 'input[name=payment_option]',
    orderForm: {
      name: '#id_name',
      phone: '#id_phone',
      email: '#id_email',
      city: '#id_city',
    },
    yandexOrderInfo: {
      customer: 'input[name=customerNumber]',
      order: 'input[name=orderNumber]',
      payment: 'input[name=paymentType]',
    },
  };

  const CONFIG = {
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
    selectSubmitBtn();
  };

  const pluginsInit = () => {
    cityAutocomplete();
  };

  const setUpListeners = () => {
    $(DOM.yandexForm).submit(() => mediator.publish('onOrderSend'));
    mediator.subscribe('onCartUpdate', renderTable, fillSavedInputs,
      touchSpinReinit, restoreSelectedPayment, cityAutocomplete);

    /**
     * Bind events to parent's elements, because we can't bind event to dynamically added element.
     */
    DOM.$order.on('click', DOM.yandexSubmit, submitYandexOrder);
    DOM.$order.on('click', DOM.remove, () => removeProduct(getElAttr(event, 'productId')));
    DOM.$order.on('click', DOM.paymentOptions, () => selectSubmitBtn(getElAttr(event, 'value')));
    DOM.$order.on('change', DOM.productCount, event => changeProductCount(event));
    DOM.$order.on('keyup', 'input', event => storeInput($(event.target)));
  };

  /**
   * Return element's attribute value by value name.
   */
  const getElAttr = (event, attributeName) => event.target.getAttribute(attributeName);

  /**
   * Init google cities autocomplete.
   */
  const cityAutocomplete = () => {
    const cityField = document.getElementById('id_city');
    if (!cityField) return;

    const cityAutocomplete = new google.maps.places.Autocomplete(cityField, CONFIG.autocomplete);

    google.maps.event.addListener(cityAutocomplete, 'place_changed', () => {
      storeInput($(DOM.orderForm.city));
    });
  };

  /**
   * Reinit touchspin plugin cause of dynamic DOM.
   */
  const touchSpinReinit = () => {
    $(DOM.productCount).TouchSpin(configs.PLUGINS.touchspin);
  };

  /**
   * Fill inputs, which have saved to localstorage value.
   * Runs on page load, and on every cart's update.
   */
  const fillSavedInputs = () => {
    const getFieldByName = (name) => $(`#id_${name}`);

    for (const fieldName in DOM.orderForm) {
      if ({}.hasOwnProperty.call(DOM.orderForm, fieldName)) {
        const $field = getFieldByName(fieldName);
        const savedValue = localStorage.getItem(fieldName);

        if ($field && savedValue) {
          $field.val(savedValue);
        }
      }
    }
  };

  /**
   * Select saved payment if there is one.
   */
  const restoreSelectedPayment = () => {
    const savedPayment = localStorage.getItem(CONFIG.paymentKey);

    if (savedPayment) {
      const isSelected = $option => $option.val() === savedPayment;

      $(DOM.paymentOptions).each((_, el) => {
        $(el).attr('checked', isSelected($(el)));
      });
    }
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
   * Select appropriate submit button, based on selected payment option.
   */
  const selectSubmitBtn = () => {
    const $yandexSubmit = $(DOM.yandexSubmit);
    const $seSubmit = $(DOM.seSubmit);
    const optionName = getSelectedPaymentName();
    const isYandexPayment = CONFIG.sePayments.indexOf(optionName) === -1;

    const selectSE = () => {
      $yandexSubmit.addClass('hidden');
      $seSubmit.removeClass('hidden');
    };

    const selectYandex = () => {
      $seSubmit.addClass('hidden');
      $yandexSubmit.removeClass('hidden');
    };

    isYandexPayment ? selectYandex() : selectSE();
    localStorage.setItem(CONFIG.paymentKey, optionName);
  };

  /**
   * Return hash with customer's info from form.
   */
  const getCustomerInfo = () => {
    const customerInfo = {};

    $.each(DOM.orderForm, (name, field) => {
      customerInfo[name] = $(field).val();
    });

    return customerInfo;
  };

  /**
   * Submit Yandex order if user's phone is provided.
   * It consists of several steps:
   *
   * 1. Get customerNumber (which is a phone without any non-numeric chars)
   * 2. Hit backend and save Order to DB. This step returns id of an order.
   * 3. Fill Yandex-form
   * 4. Submit Yandex-form.
   */
  const submitYandexOrder = event => {
    event.preventDefault();

    const getCustomerNumber = phone => phone.replace(/\D/g, '');
    const customerInfo = getCustomerInfo();
    const fillYandexForm = orderId => {
      $(DOM.yandexOrderInfo.order).val(orderId);
      $(DOM.yandexOrderInfo.customer).val(getCustomerNumber(customerInfo.phone));
      $(DOM.yandexOrderInfo.payment).val(getSelectedPaymentName());
    };

    // TODO: Form phone & mail validation need to be realize.
    // Fields should have required attr. The code locates in rf-components.
    if (!validator.isPhoneValid(customerInfo.phone)) {
      DOM.$formErrorText.removeClass('hidden').addClass('shake animated');
      return;
    }

    server.sendYandexOrder(customerInfo)
      .then(id => {
        fillYandexForm(id);
        $(DOM.yandexForm).submit();
      });
  };

  /**
   * Store inputted value into LocalStorage.
   */
  const storeInput = target => {
    localStorage.setItem(target.attr('name'), target.val());
  };

  /**
   * Remove product from cart's table and dispatches 'onCartUpdate' event.
   */
  const removeProduct = productId => {
    server.removeFromCart(productId).then(data => {
      mediator.publish('onCartUpdate', data);
    });
  };

  /**
   * Render table and form.
   * After that, fill in saved form data.
   */
  const renderTable = (event, data) => DOM.$order.html(data.table);

  init();
})();
