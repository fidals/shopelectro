/**
 * There are all common configs for all common plugins.
 * This module is an entry point for plugins initialization.
 */
const configs = (() => {
  const DOM = {
    $mobileMenu: $('#mobile-menu'),
    $modal: $('.modal'),
    $phoneInput: $('.js-masked-phone'),
    scrollWrapper: '#scroll-wrapper',
    touchspin: '.js-touchspin',
  };

  const labels = {
    callTime: 'callTime',
    phone: 'phone',
  };

  let $menu;

  const plugins = {
    scrollbar: {
      autoReinitialise: true,
      mouseWheelSpeed: 30,
    },
    touchspin: {
      min: 1,
      max: 10000,
      verticalbuttons: true,
      verticalupclass: 'glyphicon glyphicon-plus',
      verticaldownclass: 'glyphicon glyphicon-minus',
    },
    fancybox: {
      openEffect: 'fade',
      closeEffect: 'elastic',
      helpers: {
        overlay: {
          locked: false,
        },
      },
    },
  };

  const init = () => {
    pluginsInit();
    setupXHR();
    setupListeners();
  };

  function setupListeners() {
    DOM.$modal.on('shown.bs.modal', focusFirstField);
    DOM.$phoneInput.on('input', storePhoneNumber);
    DOM.$phoneInput.focus(phoneFieldFocus);
  }

  /**
   * Set all unsafe ajax requests with csrftoken.
   */
  function setupXHR() {
    const csrfUnsafeMethod = method => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
        }
      },
    });
  }

  function pluginsInit() {
    initScrollbar();
    initTouchspin();
    initMmenu();

    DOM.$phoneInput.mask('+0 (000) 000 00 00', {
      placeholder: '+7 (999) 000 00 00',
    });
  }

  function initScrollbar() {
    $(DOM.scrollWrapper).jScrollPane(plugins.scrollbar);
  }

  function initTouchspin() {
    $(DOM.touchspin).TouchSpin(plugins.touchspin);
  }

  function initMmenu() {
    $menu = DOM.$mobileMenu.mmenu({
      extensions: [
        'border-offset', 'shadow-page',
        'shadow-panels', 'effect-menu-slide',
      ],
      screenReader: true,
      navbar: {
        title: 'Меню',
      },
      navbars: [
        {
          position: 'top',
          content: ['searchfield'],
        },
      ],
      searchfield: {
        add: true,
        placeholder: 'Поиск по каталогу',
        search: false,
      },
    }, {
      offCanvas: {
        pageSelector: '#desktop-wrapper',
      },
    });
  }

  function focusFirstField(event) {
    event.target.querySelector('.form-control').focus();
  }

  function storePhoneNumber() {
    localStorage.setItem(labels.phone, $(event.target).val());
  }

  function phoneFieldFocus() {
    const $phoneInput = $(event.target);
    if (!$phoneInput.val()) $phoneInput.val('+7').trigger('change');
  }

  init();

  return {
    $menu,
    plugins,
    labels,
    initScrollbar,
    initTouchspin,
  };
})();
