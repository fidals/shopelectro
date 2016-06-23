const order = (() => {
  const DOM = {
    $fancybox: $('.fancybox'),
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
      payment: 'input[name=paymentType]'
    }
  };

  /**
   * Config object.
   * TODO: maybe we should move all the configs into separate file.
   */
  const CONFIG = {
    touchspin: {
      min: 1,
      max: 10000,
      verticalbuttons: true,
      verticalupclass: 'glyphicon glyphicon-plus',
      verticaldownclass: 'glyphicon glyphicon-minus'
    },
    fancybox: {
      openEffect: 'fade',
      closeEffect: 'elastic',
      helpers: {
        overlay: {
          locked: false
        }
      }
    },
    citiesAutocomplete: {
      types: ['(cities)'],
      componentRestrictions: {
        country: 'ru',
      },
    },
    sePayments: ['cash', 'cashless'],
    paymentKey: 'payment'
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
    fillSavedInputs();
    restoreSelectedPayment();
    selectPaymentSubmit();
  };

  /**
   * Fill inputs, which have saved to localstorage value.
   * Runs on page load, and on every cart's update.
   */
  const fillSavedInputs = () => {
    const getFieldByName = (name) => $(`#id_${name}`);

    for (let fieldName in DOM.orderForm) {
      let $field = getFieldByName(fieldName);
      let savedValue = localStorage.getItem(fieldName);
      if ($field && savedValue) {
        $field.val(savedValue);
      }
    }
  };

  /**
   * Select saved payment if there is one.
   */
  const restoreSelectedPayment = () => {
    let savedPayment = localStorage.getItem(CONFIG.paymentKey);

    if (savedPayment) {
      const isSelected = ($option) => $option.val() === savedPayment;

      $(DOM.paymentOptions).each((_, el) => {
        let $inputOption = $(el);
        $inputOption.attr('checked', isSelected($inputOption));
      });
    }
  };

  const pluginsInit = () => {
    const autocomplete = () => {
      let cityField = document.getElementById('id_city');
      if (!cityField) { return; }
      let citiesAutocomplete = new google.maps.places.Autocomplete(
        cityField, CONFIG.citiesAutocomplete);

      google.maps.event.addListener(citiesAutocomplete, 'place_changed', () => storeInput($(DOM.orderForm.city)));
    };

    const fancyBoxStart = () => {
      DOM.$fancybox.fancybox(CONFIG.fancybox);
    };

    const touchSpin = () => {
      $(DOM.productCount).TouchSpin(CONFIG.touchspin);
    };

    $(DOM.orderForm.phone).mask('+9 (999) 999 99 99');

    autocomplete();
    fancyBoxStart();
    touchSpin();
  };

  /**
   * Event handler for changing product's count in Cart.
   * We wait at least 100ms every time the user pressed the button.
   */
  const changeProductCount = (event) => {
    let productID = event.target.getAttribute('productId');
    let newCount = event.target.value;
    setTimeout(
      () => changeInCart(productID, newCount).then((data) => mediator.publish('onCartUpdate', data)),
      100
    );

  };

  /**
   * Helper function.
   * Return name (which is value) of a selected payment option.
   */
  const getSelectedPaymentName = () => {
    let $selectedOption = $(DOM.paymentOptions + ':checked');
    return $selectedOption.val();
  };

  /**
   * Select appropriate submit button, based on selected payment option.
   */
  const selectPaymentSubmit = () => {
    const selectSE = () => {
      $yandexSubmit.addClass('hidden');
      $seSubmit.removeClass('hidden');
    };

    const selectYandex = () => {
      $seSubmit.addClass('hidden');
      $yandexSubmit.removeClass('hidden');
    };

    let $yandexSubmit = $(DOM.yandexSubmit);
    let $seSubmit = $(DOM.seSubmit);
    let optionName = getSelectedPaymentName();
    let isYandexPayment = CONFIG.sePayments.indexOf(optionName) === -1;

    isYandexPayment ? selectYandex() : selectSE();
    localStorage.setItem(CONFIG.paymentKey, optionName);
  };

  /**
   * Return hash with customer's info from form.
   */
  const getCustomerInfo = () => {
    let customerInfo = {};

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
  const submitYandexOrder = (event) => {
    event.preventDefault();

    const getCustomerNumber = (phone) => phone.replace(/\D/g,'');
    const fillYandexForm = (orderId) => {
      $(DOM.yandexOrderInfo.order).val(orderId);
      $(DOM.yandexOrderInfo.customer).val(getCustomerNumber(customerInfo.phone));
      $(DOM.yandexOrderInfo.payment).val(getSelectedPaymentName());
    };

    let customerInfo = getCustomerInfo();

    if (!isPhoneValid(customerInfo.phone)) {
      // TODO: modal (Yoz)
      alert('Введите телефон.');
      return;
    }

    sendYandexOrder(customerInfo).then((id) => {
      fillYandexForm(id);
      $(DOM.yandexForm).submit();
    });

  };
  
  const setUpListeners = () => {
    /**
     * Bind events to parent's elements, because we can't bind event to dynamically added element.
     * @param eventName - standard event name
     * @param element - element, which is a child of parent's element (DOM.$order)
     * @param handler - callable which will be dispatched on event
     */
    const subscribeOrderEvent = (eventName, element, handler) => DOM.$order.on(eventName, element, handler);
    let getEventTarget = (event) => $(event.target);
    
    subscribeOrderEvent('change', DOM.productCount, (event) => changeProductCount(event));
    subscribeOrderEvent('click', DOM.remove, (event) => remove(event.target.getAttribute('productId')));
    subscribeOrderEvent('keyup', 'input', (event) => storeInput(getEventTarget(event)));
    subscribeOrderEvent('click', DOM.paymentOptions, (event) => selectPaymentSubmit(event.target.getAttribute('value')));
    subscribeOrderEvent('click', DOM.yandexSubmit, submitYandexOrder);
    
    mediator.subscribe('onCartUpdate', renderTable, pluginsInit);
  };

  /**
   * Store inputted value into LocalStorage.
   */
  const storeInput = (target) => {
    localStorage.setItem(target.attr('name'), target.val());
  };

  /**
   * Remove product from cart's table and dispatches 'onCartUpdate' event.
   */
  const remove = (productId) => {
    removeFromCart(productId).then((data) => {
      mediator.publish('onCartUpdate', data);
    })
  };
  
  /**
   * Render table and form.
   * After that, fill in saved form data.
   */
  const renderTable = (event, data) => {
    DOM.$order.html(data.table);
    fillSavedInputs();
    restoreSelectedPayment();
    selectPaymentSubmit();
  };

  init();
})();
