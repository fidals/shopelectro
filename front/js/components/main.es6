const DOM = {
  phoneInputs: $('.js-masked-phone'),
  btnScrollTop: $('#btn-scroll-to-top'),
  scrollWrapper: $('#scroll-wrapper'),
  inputTouchspin: $('.js-touchspin'),
};

const BACKCALL_MODAL = {
  closeTag: $('.js-backcall-close'),
  phoneTag: $('#back-call-phone'),
  sendBtn: $('.js-send-backcall'),
  successTag: $('.js-backcall-success'),
  timeText: $('.js-backcall-time'),
  timeTag: $('.js-select-time'),
  timeToCall: $('#back-call-time'),
  isSend: false,

  /**
   * Handles 'Backcall order' form.
   */
  sendBackcall: () => {
    let data = {
      phone: BACKCALL_MODAL.phoneTag.val(),
      time: BACKCALL_MODAL.timeToCall.val(),
    };

    SEND_BACKCALL(data)
      .then(() => {
        BACKCALL_MODAL.timeText.text(BACKCALL_MODAL.timeTag.val());
        BACKCALL_MODAL.showSuccessModal();
      }, (response) => {
        console.group();
        console.warn('Something goes wrong...');
        console.log(response);
        console.groupEnd();
      });
  },

  /**
   * Toggles backcall form buttons state.
   */
  showSuccessModal: () => {
    BACKCALL_MODAL.sendBtn.toggleClass('hidden');
    BACKCALL_MODAL.closeTag.toggleClass('hidden');
    BACKCALL_MODAL.successTag
      .toggleClass('hidden')
      .siblings().toggleClass('hidden');
    BACKCALL_MODAL.isSend = true;
  },
};

const USER_BACKCALL_TIME = 'userBackcallTime';
const USER_PHONE = 'userPhone';

let init = () => {
  pluginsInit();
  fillInUserData({
    USER_PHONE: localStorage.getItem(USER_PHONE),
    USER_BACKCALL_TIME: localStorage.getItem(USER_BACKCALL_TIME),
  });
  setUpListeners();
};

let setUpListeners = () => {
  $(window).scroll(toggleToTopBtn);
  BACKCALL_MODAL.sendBtn.on('click', BACKCALL_MODAL.sendBackcall);
  BACKCALL_MODAL.timeTag.on('change', storeBackcallTime.bind(this));
  DOM.btnScrollTop.on('click', () => $('html, body').animate({ scrollTop: 0 }, 300));
};

let pluginsInit = () => {
  /**
   * Initializes masks for phone input fields.
   */
  DOM.phoneInputs
    .mask('+9 (999) 999 99 99')
    .on('keyup', function () {
      localStorage.setItem(USER_PHONE, $(this).val());
    });

  /**
   * Initializes custom scrollbar.
   */
  DOM.scrollWrapper.jScrollPane({
    autoReinitialise: true,
    mouseWheelSpeed: 30,
  });

  /**
   * Initializes TouchSpin for product count inputs.
   */
  DOM.inputTouchspin.TouchSpin({
    min: 1,
    max: 10000,
    verticalbuttons: true,
    verticalupclass: 'glyphicon glyphicon-plus',
    verticaldownclass: 'glyphicon glyphicon-minus',
  });
};

let fillInUserData = (data) => {
  /**
  * Sets up user phone number.
  */
  if (data.USER_PHONE) {
    $.each(DOM.phoneInputs, function () {
      $(this).val(data.USER_PHONE);
    });
  }

  /**
  * Sets up user backcall time.
  */
  if (data.USER_BACKCALL_TIME) {
    BACKCALL_MODAL.timeTag.find('[data-time=' + data.USER_BACKCALL_TIME + ']').attr('selected', true);
  }
};

/**
 * Toggles to top button.
 */
let toggleToTopBtn = () => {
  if ($(window).scrollTop() > 300) {
    DOM.btnScrollTop.addClass('active');
  } else {
    DOM.btnScrollTop.removeClass('active');
  }
};

/**
 * Stores users time for backcall.
 */
let storeBackcallTime = (selectedOption) => {
  let selectedTime = $(selectedOption.target).find(':selected').data('time');
  localStorage.setItem(USER_BACKCALL_TIME, selectedTime);
};

init();
