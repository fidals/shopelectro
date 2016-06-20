const orderCall = (() => {
  const DOM = {
    phoneInputs: $('.js-masked-phone'),
    closeModal: $('.js-backcall-close'),
    phone: $('#back-call-phone'),
    orderButton: $('.js-send-backcall'),
    successTag: $('.js-backcall-success'),
    timeText: $('.js-backcall-time'),
    timeTag: $('.js-select-time'),
    timeToCall: $('#back-call-time')
  };

  const CONFIG = {
    isSend: false,
    callTime: 'callTime',
    phone: 'phone'
  };

  const init = () => {
    fillInUserData({
        phone: localStorage.getItem(CONFIG.phone),
        time: localStorage.getItem(CONFIG.callTime)
    });
    pluginsInit();
    setUpListeners();
  };

  const pluginsInit = () => {
    DOM.phoneInputs
      .mask('+9 (999) 999 99 99')
      .on('keyup', function () {
        localStorage.setItem(CONFIG.phone, $(this).val());
      });
  };

  const setUpListeners = () => {
      DOM.orderButton.on('click', order);
      DOM.timeTag.on('change', storeBackcallTime.bind(this));
  };

  const fillInUserData = data => {
    if (data.phone) {
      $.each(DOM.phoneInputs, () => {
        $(this).val(data.phone);
      });
    }
    if (data.time) {
      DOM.timeTag.find('[data-time=' + data.time + ']').attr('selected', true);
    }
  };

  const order = () => {
    let phone = DOM.phone.val();
    let time = DOM.timeToCall.val();
    let url = location.href;

    server.sendOrderCall(phone, time, url).then(() => {
      DOM.timeText.text(DOM.timeTag.val());
      showSuccessModal();
    });
  };

  const showSuccessModal = () => {
    DOM.orderButton.toggleClass('hidden');
    DOM.closeModal.toggleClass('hidden');
    DOM.successTag
      .toggleClass('hidden')
      .siblings().toggleClass('hidden');
    CONFIG.isSend = true;
  };

  const storeBackcallTime = (selectedOption) => {
    let selectedTime = $(selectedOption.target).find(':selected').data('time');
    localStorage.setItem(CONFIG.callTime, selectedTime);
  };

  init();
})();
