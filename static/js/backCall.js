var backCall = (function ($) {
  var $backCall = $('#back-call');
  var $successModal = $('#back-call-success');
  var $uiOverlay = $('.ui-widget-overlay');

  var init = (function () {
    $backCall.dialog({
      autoOpen: false,
      resizable: false,
      modal: true,
      draggable: false,
      open: function () {
        $uiOverlay.on('click', function () {
          $backCall.dialog('close');
        });

        yaCounter20644114.reachGoal('BACK_CALL_OPEN');
      },
    });

    $successModal.dialog({
      autoOpen: false,
      resizable: false,
      modal: true,
      draggable: false,
      open: function () {
        $uiOverlay.on('click', function () {
          $backCall.dialog('close');
        });

        setTimeout(function () {
          $successModal.dialog('close');
        }, 30000);
      },

      close: function () {
      },
    });

    $('#back-call-opener, #article-back-call-opener').on('click', function () {
      $backCall.dialog('open');
    });
  })();

  return {
    view: {
      /**
       * Выводит текст успешной заявки:
       *
       * @param time;
       */
      responseSuccess: function (time) {
        $backCall.dialog('close');
        $successModal
          .dialog('open')
          .find('.time').text(time);
      },

      /**
       * Выводит сообщение при ошибке ввода телефонного номера:
       */
      phoneValidationFail: function () {
        $backCall.children('.error-msg').text('Укажите телефон');
      },
    },

    controller: {
      /**
       * Обрабатывае форму заявки 'Заказать звонок':
       *
       * @param phone;
       * @param time;
       */
      sendBackCall: function (phone, time) {
        var url = document.URL;

        if (service.main.isPhoneValid(phone)) {
          service.backCall.backCallRequest(phone, time, url, function () {
            common.backCall.view.responseSuccess(time);

            yaCounter20644114.reachGoal('BACK_CALL_SEND');
          });
        } else {
          common.backCall.view.phoneValidationFail();
        }
      },
    },
  };
}(jQuery));
