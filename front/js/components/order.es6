const order = (() => {
  const DOM = {
    fancybox: $('.fancybox'),
    productCount: '.prod-count',
    remove: '.btn-cart',
    totalCount: $('.order-count'),
    totalPrice: $('.order-sum'),
    order: $('.js-order-contain'),
    orderForm: {
      name: $('#id_name'),
      phone: $('#id_phone'),
      email: $('#id_email'),
      city: $('#id_city'),
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
    }
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
    fillInputs();
  };

  /**
   * Fill inputs of a form.
   * Implemented without jQuery because it badly handles dynamically added
   * elements.
   */
  const fillInputs = () => {
    let getFieldByName = (name) => document.getElementById(`id_${name}`);

    for (let fieldName in DOM.orderForm) {
      let field = getFieldByName(fieldName);
      let savedValue = localStorage.getItem(fieldName);
      if (savedValue) {
        field.value = savedValue;
      }
    }
  };

  const pluginsInit = () => {
    const autocomplete = () => {
      let citiesAutocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_city'), CONFIG.citiesAutocomplete);

      google.maps.event.addListener(citiesAutocomplete, 'place_changed', function () {
        storeInput(DOM.orderForm.city);
      });
    };

    const fancyBoxStart = () => {
      DOM.fancybox.fancybox(CONFIG.fancybox);
    };

    const touchSpin = () => {
      $(DOM.productCount).TouchSpin(CONFIG.touchspin);
    };

    DOM.orderForm.phone.mask('+9 (999) 999 99 99');

    autocomplete();
    fancyBoxStart();
    touchSpin();
  };

  /**
   * Event handler for changing product's count in Cart.
   * We wait at least 100ms every time the user pressed the button.
   * @param event
   */
  const changeProductCount = (event) => {
    let productID = event.target.getAttribute('productId');
    let newCount = event.target.value;
    setTimeout(
      changeInCart(productID, newCount).then((data) => mediator.publish('onCartUpdate', data)),
      100
    );

  };

  /**
   * We bind events to parent's elements, because we can't bind event to dynamically
   * added element.
   */
  const setUpListeners = () => {
    DOM.order.on('change', DOM.productCount, (event) => setTimeout(changeProductCount(event), 100));
    DOM.order.on('click', DOM.remove, (event) => remove(event.target.getAttribute('productId')));
    DOM.order.on('keyup', 'input', (event) => storeInput($(event.target)));
    mediator.subscribe('onCartUpdate', renderTable, pluginsInit);
  };

  /**
   * Stores inputted value into LocalStorage.
   * TODO: maybe we should move all the LS-logic into separate file, also.
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
   * Renders table and form.
   * After that, fill in saved form data.
   */
  const renderTable = (event, data) => {
    DOM.order.html(data.table);
    fillInputs();
  };

  init();
})();
