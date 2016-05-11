const DOM = {
  'phoneInputs': $('.js-masked-phone'),
  'btnScrollTop': $('#btn-scroll-to-top'),
  'btnSendBackcall': $('.js-send-backcall'),
  'userSelectTime': $('.js-select-time'),
};
const BACKCALL_MODAL = {
  'timeToCall': $('#back-call-time'),
  'isSend': false,

  /**
   * Handles 'Backcall order' form:
   */
  sendBackcall: () => {
    let data = {
      'phone': $('#back-call-phone').val(),
      'time': BACKCALL_MODAL.timeToCall.val(),
    };

    SEND_BACKCALL(data)
      .then(() => {
        $('.js-backcall-time').text(DOM.userSelectTime.val());
        BACKCALL_MODAL.showSuccessModal();
      }, (response) => {
        console.group();
        console.warn('Something goes wrong...');
        console.log(response);
        console.groupEnd();
      });
  },

  /**
   * Toggles backcall form buttons state:
   */
  showSuccessModal: () => {
    DOM.btnSendBackcall.toggleClass('hidden');
    $('.js-send-backcall-text').toggleClass('hidden');
    $('.js-backcall-success')
      .toggleClass('hidden')
      .siblings().toggleClass('hidden');
    BACKCALL_MODAL.isSend = true;
  },
};
const USER_BACKCALL_TIME = 'userBackcallTime';
const USER_PHONE = 'userPhone';

let initialization = () => {
  pluginsInit();
  fillInUserData({
    USER_PHONE: localStorage.getItem(USER_PHONE),
    USER_BACKCALL_TIME: localStorage.getItem(USER_BACKCALL_TIME)
  });
  setUpListeners();
};

let setUpListeners = () => {
  $(window).scroll(toggleToTopBtn);
  DOM.btnSendBackcall.on('click', BACKCALL_MODAL.sendBackcall);
  DOM.userSelectTime.on('change', storeTimeToBackcall.bind(this));
  DOM.btnScrollTop.on('click', () => $('html, body').animate({ scrollTop: 0 }, 300));
};

let pluginsInit = () => {
  /**
   * Initializes masks for phone input fields with +7 on focus:
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
   * Initializes custom scrollbar:
   */
  $('#scroll-wrapper').jScrollPane({
    autoReinitialise: true,
    mouseWheelSpeed: 30,
  });
};

/**
* Sets up user phone number:
*/
let fillInUserData = (data) => {
  if (data.USER_PHONE) {
    $.each(DOM.phoneInputs, function () {
      $(this).val(data.USER_PHONE);
    });
  }

  /**
   * Устанавлмвает время перезвона:
   */
  if (data.USER_BACKCALL_TIME) {
    DOM.userSelectTime.find('[data-time=' + data.USER_BACKCALL_TIME + ']').attr('selected', true);
  }
};

/**
 * Toggles to top button:
 */
let toggleToTopBtn = () => {
  if ($(window).scrollTop() > 100) {
    DOM.btnScrollTop.addClass('active');
  } else {
    DOM.btnScrollTop.removeClass('active');
  }
};

/**
 * Stores users time for backcall:
 */
let storeTimeToBackcall = (clickedOption) => {
  let selectedTime = $(clickedOption.target).find(':selected').data('time');
  localStorage.setItem(USER_BACKCALL_TIME, selectedTime);
};

initialization();
