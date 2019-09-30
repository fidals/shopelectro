(() => {
  const DOM = {
    $phone: $('#back-call-phone'),
    $callModal: $('#back-call-modal'),
    $closeModalBtn: $('.js-backcall-close'),
    $orderBtn: $('.js-send-backcall'),
    $successTag: $('.js-backcall-success'),
    $timeText: $('.js-backcall-time'),
    $timeTag: $('.js-select-time'),
    $timeToCall: $('#back-call-time'),
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onBackCallSend', showSuccessModal);

    DOM.$orderBtn.click(orderCall);
    DOM.$timeTag.change(storeBackcallTime);
  }

  function orderCall() {
    const phone = DOM.$phone.val();
    const time = DOM.$timeToCall.val();
    const url = window.location.href;
    const isPhoneValid = helpers.isPhoneValid(phone);

    if (!isPhoneValid) {
      DOM.$phone
        .addClass('shake animated')
        .closest('.form-group').addClass('has-error');
      return;
    }

    helpers.setDisabledState(DOM.$orderBtn);

    server.sendOrderCall(phone, time, url)
      .then(() => {
        DOM.$timeText.text(DOM.$timeTag.val());
        mediator.publish('onBackCallSend', phone);
      });
  }

  function showSuccessModal() {
    DOM.$orderBtn.addClass('hidden');
    DOM.$closeModalBtn.removeClass('hidden');
    DOM.$successTag
      .removeClass('hidden')
      .siblings().addClass('hidden');
  }

  function storeBackcallTime(event) {
    const selectedTime = $(event.target).find(':selected').data('time');
    localStorage.setItem(configs.labels.callTime, selectedTime);
  }

  init();
})();
