const DOM = {
  'phoneInputs': $('.js-masked-phone'),
  'btnScrollTop': $('#btn-scroll-to-top'),
  'btnSendCallback': $('.js-send-callback'),
  'userSelectTime': $('.js-select-time'),
};
const USER_CALLBACK_TIME = 'userCallbackTime';
const USER_PHONE = 'userPhone';

let initialization = () => {
  pluginsInit();
  fillInUserData({
    USER_PHONE : localStorage.getItem(USER_PHONE),
    USER_CALLBACK_TIME : localStorage.getItem(USER_CALLBACK_TIME)
  });
  setUpListeners();
};

let setUpListeners = () => {
  DOM.btnSendCallback.on('click', sendCallback.bind(this, {
    'phone': $('#back-call-phone').val(),
    'time': DOM.userSelectTime.val(),
  }));
  $(window).scroll(toggleToTopBtn);
  DOM.userSelectTime.on('change', storeTimeToCallback.bind(this));
  DOM.btnScrollTop.on('click', () => $('html, body').animate({ scrollTop: 0 }, 300));
  $('#back-call-modal').on('hidden.bs.modal', resetCallbackBtnsState);
};

let pluginsInit = () => {
  /**
   * Инициализирует маски для полей ввода телефонных номеров с +7 при фокусе:
   */
  DOM.phoneInputs
    .mask('+9 (999) 999 99 99')
    .on('focus', () => {
      if (!$(this).val()) {
        $(this).val('+7');
      }
    })
    .on('keyup', function () {
      localStorage.setItem(USER_PHONE, $(this).val())
    });

  /**
   * Инициализирует кастомный скроллбар:
   */
  $('#scroll-wrapper').jScrollPane({
    autoReinitialise: true,
    mouseWheelSpeed: 30,
  });
};

let fillInUserData = (data) => {
  /**
  * Устанавливает номер телефона пользователя:
  */
  if (data.USER_PHONE) {
    $.each(DOM.phoneInputs, function () {
      $(this).val(data.USER_PHONE);
    });
  }

  /**
   * Устанавлмвает время перезвона:
   */
  if (data.USER_CALLBACK_TIME) {
    DOM.userSelectTime.find('[data-time=' + data.USER_CALLBACK_TIME + ']').attr('selected', true);
  }
};

/**
 * Показывает\скрывает кнопку Наверх:
 */
let toggleToTopBtn = () => {
  if ($(window).scrollTop() > 100) {
    DOM.btnScrollTop.addClass('active');
  } else {
    DOM.btnScrollTop.removeClass('active');
  }
};

/**
 * Сохраняет время для перезвона:
 */
let storeTimeToCallback = (clickedOption) => {
  let selectedTime = $(clickedOption.target).find(':selected').data('time');
  localStorage.setItem(USER_CALLBACK_TIME, selectedTime);
};

/**
 * Обрабатывает форму заявки 'Заказать звонок':
 */
let sendCallback = (data) => {
  SEND_CALLBACK(data)
    .then((response) => {
      $('.js-callback-time').text(DOM.userSelectTime.val());
      toggleCallbackBtnsState();
    })
    .catch((err) => {
      console.log(err);
    });
};

/**
 * Изменяет состояние кнопок формы перезвона:
 */
let toggleCallbackBtnsState = () => {
  DOM.btnSendCallback.toggleClass('hidden');
  $('.js-send-callback-text').toggleClass('hidden');
  $('.js-callback-success')
    .toggleClass('hidden')
    .siblings().toggleClass('hidden');
};

/**
 * Изменяет состояние кнопок формы перезвона:
 */
let resetCallbackBtnsState = () => {
  if (DOM.btnSendCallback.hasClass('hidden')) {
    toggleCallbackBtnsState();
  }
};

initialization();
