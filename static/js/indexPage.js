var indexPage = (function ($) {
  var $backCallTime = $('#back-call-time');      // время для перезвона;
  var $backCallPhone = $('#back-call-phone');    // телефон для перезвона;
  var $inputForTouchspin = $('.js-touchspin');   // поля ввода кол-ва товара;
  var $scrollWrapper = $('#scroll-wrapper');     // обертка для кастомного скроллбара;
  var $phoneInputs = $('.js-masked-phone');      // поля ввода телефона;
  var $searchInput = $('.js-search-input');      // поле поиска в шапке;
  var $btnScrollToTop = $('#btn-scroll-to-top'); // кнопка прокрутки наверх;
  var autocompleteResults;
  var userPhone = localStorage.getItem('userPhone');
  var userTimeToCall = localStorage.getItem('userTimeToCallBack');

  var init = function () {
    /**
     * Глобальная переменная для Я.Метрики:
     */
    window.dataLayer = window.dataLayer || [];

    /**
     * Инициализирует плагин Autocomplete:
     */
    $searchInput
      .autocomplete({
        source: '/catalog/search/autocomplete/',
        minLength: 2,
        response: function (event, ui) {
          autocompleteResults = ui.content;
        },
      })

      .data('ui-autocomplete')._renderItem = function (ul, item) {
        var anchorHtml = '';
        var $listItem = $('<li>');

        if (item.url === 'see other...') {
          anchorHtml = '<div class="ui-corner-all" id="search-see-all"' +
            'onclick="$(\'#search-submit\').trigger(\'click\')">' + item.label + '</div>';
        } else {
          anchorHtml = '<a href="' + item.url   + '">' +
                  '<span>' + item.label + '</span>';

          if (item.price !== undefined) {
            anchorHtml += '<span>' + item.price + ' руб.' + '</span>';
          }

          anchorHtml += '</a>';
        }

        $listItem.append(anchorHtml).data('ui-autocomplete-item', item);

        return $listItem.appendTo(ul);
      };

    /**
     * Инициализирует плагин jQueryMask.
     * Делает маски для полей ввода телефонных номеров с +7 при фокусе:
     */
    $phoneInputs
      .mask('+9 (999) 999 99 99')
      .on('focus', function () {
        if (!$(this).val()) {
          $(this).val('+7');
        }
      })
      .on('keyup', function () {
        controller.storePhoneToCall($(this).val());
      });

    if (userPhone) {
      $.each($phoneInputs, function () {
        $(this).val(userPhone);
      });
    }

    /**
     * Инициализирует плагин jScrollPane для сквозной выпадашки корзины:
     */
    $scrollWrapper.jScrollPane({
      autoReinitialise: true,
      mouseWheelSpeed: 30,
    });

    /**
     * Инициализирует плагин TouchSpin для полей ввода кол-ва товара:
     */
    $inputForTouchspin.TouchSpin({
      min: 1,
      max: 10000,
      verticalbuttons: true,
      verticalupclass: 'glyphicon glyphicon-plus',
      verticaldownclass: 'glyphicon glyphicon-minus',
    });

    /**
     * Отправляет метрику при уменьшении кол-ва товаров с помощью TouchSpin:
     */
    $inputForTouchspin.on('touchspin.on.stopdownspin', function () {
      yaCounter20644114.reachGoal('DELETE_PRODUCT');
    });

    /**
     * Показывает\скрывает кнопку Наверх:
     */
    $(window).scroll(function () {
      if ($(this).scrollTop() > 300) {
        $btnScrollToTop.addClass('active');
      } else {
        $btnScrollToTop.removeClass('active');
      }
    });

    /**
     * Устанавливает время перезвона в окне 'Заказать звонок':
     */
    if (userTimeToCall) {
      view.restoreTimeToCall();
    }
  };

  var view = {
    /**
     * Прокручивает страницу наверх:
     */
    scrollToTop: function () {
      $('html, body').animate({ scrollTop: 0 }, 800);

      return false;
    },

    /**
     * Вставляет пример текста для поиска в поле поиска и вызывает метод поиска:
     *
     * @param target;
     */
    searchBySampleText: function (target) {
      $searchInput
        .val($(target).text())
        .autocomplete('search')
        .focus();
    },

    /**
     * Инициализирует плагин Fancybox:
     */
    fancyBoxInit: function () {
      $('.fancybox').fancybox({
        openEffect: 'fade',
        closeEffect: 'elastic',
        helpers: {
          overlay: {
            locked: false,
          },
        },
      });
    },

    /**
     * Изменяет время перезвона:
     */
    restoreTimeToCall: function () {
      $backCallTime.find('[data-time=' + userTimeToCall + ']').attr('selected', true);
    },
  };

  var controller = {
    /**
     * Отправляет метрику и делает запись в локальном хранилище,
     * если пользователь скопировал адрес почты полностью:
     */
    copyEmail: function () {
      var selectedText = service.main.getSelectionText();
      var textTarget     = 'info@shopelectro.ru';
      var textMatched    = selectedText.indexOf(textTarget);
      var wasEmailCopied = localStorage.getItem('mailIsCopied');

      if (textMatched === 0 && wasEmailCopied !== 'true') {
        localStorage.setItem('mailIsCopied', 'true');

        yaCounter20644114.reachGoal('COPY_MAIL');
      }
    },

    /**
     * Отправляет метрику и делает запись в локальном хранилище,
     * если пользователь скопировал номер телефона полностью:
     */
    copyPhone: function () {
      var selectedText    = service.main.getSelectionText();
      var regexpPhoneCopy = /\d{3}-\d{2}-\d{2}/g;
      var isTextMatched   = !!selectedText.match(regexpPhoneCopy);
      var wasPhoneCopied  = localStorage.getItem('phoneIsCopied');

      if (isTextMatched && wasPhoneCopied !== 'true') {
        localStorage.setItem('phoneIsCopied', 'true');

        yaCounter20644114.reachGoal('COPY_PHONE');
      }
    },

    /**
     * Отправляет метрику при просмотре продукта
     */
    reachProdBrowseGoal: function () {
      yaCounter20644114.reachGoal('PROD_BROWSE');
    },

    /**
     * Перенаправляет на страницу единственно найденного товара
     * по клику на кнопку "Найти":
     */
    searchBtnRedirect: function () {
      if (autocompleteResults.length === 1) {
        event.preventDefault();
        window.location.pathname = autocompleteResults[0].url;
      }
    },

    /**
     * Перенаправляет на страницу единственно найденного товара
     * по клику на Enter:
     */
    searchEnterRedirect: function (event) {
      if (event.which === 13) {
        if (autocompleteResults.length === 1) {
          event.preventDefault();
          window.location.pathname = autocompleteResults[0].url;
        }
      }
    },

    /**
     * Отправляет письмо из окна "Перезвоните мне" по клику на Enter:
     */
    backCallFormSubmit: function (e) {
      e.preventDefault();
      common.backCall.controller.sendBackCall($backCallPhone.val(), $backCallTime.val());
    },

    /**
     * Сохраняет время перезвона:
     */
    storeTimeToCall: function (selectedId) {
      localStorage.setItem('userTimeToCallBack', selectedId);
    },

    /**
     * Сохраняет время перезвона:
     */
    storePhoneToCall: function (phone) {
      localStorage.setItem('userPhone', phone);
    },
  };

  init();

  return {
    view: view,
    controller: controller,
  };
}(jQuery));
