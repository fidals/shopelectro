/**
 * There are all common configs for all common plugins.
 * This module is an entry point for plugins initialization.
 */
const configs = (() => {
  const DOM = {
    scrollWrapper: '#scroll-wrapper',
    $touchspin: $('.js-touchspin'),
    $phoneInputs: $('.js-masked-phone'),
  };

  const LABELS = {
    callTime: 'callTime',
    phone: 'phone',
  };

  const PLUGINS = {
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
  const setupXHR = () => {
    const csrfUnsafeMethod = method => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
        }
      },
    });
  };

  const pluginsInit = () => {
    $(DOM.scrollWrapper).jScrollPane(PLUGINS.scrollbar);
    DOM.$touchspin.TouchSpin(PLUGINS.touchspin);

    DOM.$phoneInputs
      .attr('placeholder', '+7 (999) 000 00 00')
      .mask('+9 (999) 999 99 99')
      .on('keyup', (event) => {
        localStorage.setItem(LABELS.phone, $(event.target).val());
      });
  };

  const scrollbarReinit = () => $(DOM.scrollWrapper).jScrollPane(PLUGINS.scrollbar);

  init();

  return { PLUGINS, setupXHR, LABELS, scrollbarReinit };
})();
