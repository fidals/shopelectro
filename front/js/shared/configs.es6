/**
 * There are all common configs for all common plugins.
 * This module is an entry point for plugins initialization.
 */
const configs = (() => {
  const DOM = {
    scrollWrapper: '#scroll-wrapper',
    touchspin: '.js-touchspin',
    $phoneInputs: $('.js-masked-phone'),
  };

  const labels = {
    callTime: 'callTime',
    phone: 'phone',
  };

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
  };

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

    DOM.$phoneInputs
      .mask('+0 (000) 000 00 00', {
        placeholder: '+7 (999) 000 00 00',
      })
      .on('change', event => {
        localStorage.setItem(labels.phone, $(event.target).val());
      })
      .on('click', event => {
        const $phoneInput = $(event.target);
        if (!$phoneInput.val()) $phoneInput.val('+7').trigger('change');
      });
  }

  function initScrollbar() {
    $(DOM.scrollWrapper).jScrollPane(plugins.scrollbar);
  }

  function initTouchspin() {
    $(DOM.touchspin).TouchSpin(plugins.touchspin);
  }

  init();

  return {
    plugins,
    labels,
    initScrollbar,
    initTouchspin,
  };
})();
