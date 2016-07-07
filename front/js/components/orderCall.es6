const orderCall = (() => {
  const DOM = {
    $phone: $('#back-call-phone'),
    $callModal: $('#back-call-modal'),
    $phoneInputs: $('.js-masked-phone'),
    $closeModal: $('.js-backcall-close'),
    $orderButton: $('.js-send-backcall'),
    $successTag: $('.js-backcall-success'),
    $timeText: $('.js-backcall-time'),
    $timeTag: $('.js-select-time'),
    $timeToCall: $('#back-call-time'),
  };

  const CONFIG = {
    isSend: false,
    callTime: 'callTime',
    phone: 'phone',
  };

  const init = () => {
    fillInUserData({
        phone: localStorage.getItem(CONFIG.phone),
        time: localStorage.getItem(CONFIG.callTime),
    });
    pluginsInit();
    setUpListeners();
  };

  const pluginsInit = () => {
    DOM.$phoneInputs
      .attr('placeholder', '+7 (999) 000 00 00')
      .mask('+9 (999) 999 99 99')
      .on('keyup', () => {
        localStorage.setItem(CONFIG.phone, $(this).val());
      });
  };

  const setUpListeners = () => {
    DOM.$orderButton.on('click', order);
    DOM.$timeTag.on('change', storeBackcallTime.bind(this));
    DOM.$callModal.on('hidden.bs.modal', resetModal);
  };

  const fillInUserData = data => {
    if (data.phone) {
      $.each(DOM.$phoneInputs, () => {
        $(this).val(data.phone);
      });
    }
    if (data.time) {
      DOM.$timeTag.find('[data-time=' + data.time + ']').attr('selected', true);
    }
  };

  const order = () => {
    const phone = DOM.$phone.val();
    const time = DOM.$timeToCall.val();
    const url = location.href;

    if (!validator.isPhoneValid(phone)) {
      DOM.$phone
        .addClass('shake animated')
        .closest('.form-group').addClass('has-error');
      return;
    }

    server.sendOrderCall(phone, time, url).then(() => {
      DOM.$timeText.text(DOM.$timeTag.val());
      CONFIG.isSend = true;

      toggleSuccessModal();
      yaCounter20644114.reachGoal('BACK_CALL_SEND');
    });
  };

  const toggleSuccessModal = () => {
    DOM.$orderButton.toggleClass('hidden');
    DOM.$closeModal.toggleClass('hidden');
    DOM.$successTag
      .toggleClass('hidden')
      .siblings().toggleClass('hidden');
  };

  const resetModal = () => {
    DOM.$phone
      .removeClass('shake animated')
      .closest('.form-group').removeClass('has-error');

    if (CONFIG.isSend) {
      CONFIG.isSend = false;
      toggleSuccessModal();
    }
  };

  const storeBackcallTime = (selectedOption) => {
    const selectedTime = $(selectedOption.target).find(':selected').data('time');

    localStorage.setItem(CONFIG.callTime, selectedTime);
  };

  init();
})();
