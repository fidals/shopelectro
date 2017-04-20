(() => {
  const DOM = {
    $imageBig: $('#product-image-big'),
    $imagesToSwitch: $('.js-image-switch'),
    $fancybox: $('.fancybox'),
    $addToCart: $('#btn-to-basket'),
    $phone: $('#input-one-click-phone'),
    $oneClick: $('#btn-one-click-order'),
    $counter: $('#product-count'),
    $product_text: $('.product-text'),

    // Feedback DOM elements
    field: '.js-modal-field',
    filledRatingIcon: 'rating-icon-full',
    emptyRatingIcon: 'rating-icon-empty',
    $closeModalBtn: $('.js-modal-close'),
    $feedbackBtn: $('.js-send-feedback'),
    $feedbackDelete: $('.js-feedback-delete'),
    $feedbackList: $('#feedbacks-list'),
    $feedbackModal: $('#product-feedback-modal'),
    $feedbackNameField: $('#feedback-modal-name'),
    $ratingFilter: $('.js-rating-filter'),
    $ratingList: $('.js-rating'),
    $successModalText: $('.js-feedback-success'),
  };

  const productId = DOM.$addToCart.attr('data-id');

  const init = () => {
    shorten();
    setUpListeners();
    changeOneClickBtnState();
  };

  function setUpListeners() {
    mediator.subscribe('onOneClickBuy', successOrder);

    // Feedback events
    mediator.subscribe('onFeedbackSave', feedbackSavedResponse);
    mediator.subscribe('onFeedbackDelete', feedbackDeleteResponse);
    mediator.subscribe('onRate', changeRateIcons, setBtnActiveState);

    DOM.$imageBig.click(fancyBoxStart);
    DOM.$imagesToSwitch.click(productImgSwitch);
    DOM.$addToCart.click(buyProduct);
    DOM.$oneClick.click(oneClick);
    DOM.$feedbackBtn.click(sendFeedback);
    DOM.$feedbackDelete.click(deleteFeedback);
    DOM.$phone.keyup(changeOneClickBtnState);
    DOM.$ratingList.on('click', 'li', () => mediator.publish('onRate', event));
    DOM.$ratingFilter.on('click', '.js-filter-trigger', filterByRating);
    $('.js-more-text').on('click', truncateDescription);
  }

  /**
   * Initialize fancyBox on specific index image.
   */
  function fancyBoxStart() {
    $.fancybox(
      DOM.$fancybox, {
        index: DOM.$imageBig.attr('data-index'),
        helpers: {
          overlay: {
            locked: false,
          },
        },
      });

    return false; // this return is required
  }

  /**
   * Send product data & redirect page.
   */
  function oneClick() {
    helpers.setDisabledState(DOM.$oneClick, 'Ожидайте...');

    server.oneClickBuy(productId, DOM.$counter.val(), DOM.$phone.val())
      .then(() => mediator.publish('onOneClickBuy'));
  }

  function changeOneClickBtnState() {
    if (DOM.$oneClick.size() > 0) {
      DOM.$oneClick.attr('disabled', !helpers.isPhoneValid(DOM.$phone.val()));
    }
  }

  function shorten() {
    const showChars = 140;
    const minChars = 10;
    const ellipses = '...';

    return DOM.$product_text.each(function () {
      const $this = $(this);
      if ($this.hasClass('shortened')) {
        return;
      }
      $this.addClass('shortened');

      const text = $this.text();
      const textLen = text.length;

      if (textLen > showChars + minChars) {
        const nextSpaceIndex = text.substr(showChars, textLen - showChars).indexOf(' ');
        const numberOfVisible = parseInt(showChars, 10) + parseInt(nextSpaceIndex, 10);
        const visibleText = text.substr(0, numberOfVisible);
        const invisibleText = text.substr(numberOfVisible, textLen - numberOfVisible);

        $this.html(`
          <span class="short-content">${visibleText}</span>
          <span>${ellipses}&nbsp;</span>
          <span class="more-content">${invisibleText}&nbsp;</span>
          <a href="#" class="js-more-text">Больше</a>
        `);
        $this.find('.more-content').hide();
      }
    });
  }

  /**
   * Switch product images.
   *
   * @param event - click on image preview;
   */
  function productImgSwitch(event) {
    const targetSrc = $(event.target).attr('src');
    const dataIndex = $(event.target).attr('data-index');

    if (targetSrc !== DOM.$imageBig.attr('src')) {
      DOM.$imageBig.attr({
        src: targetSrc,
        'data-index': dataIndex,
      });
    }
  }

  function buyProduct() {
    const { id, count } = {
      id: productId,
      count: DOM.$counter.val(),
    };

    server.addToCart(id, count)
      .then(data => mediator.publish('onCartUpdate', data));
  }

  function successOrder() {
    location.href = '/shop/order-success';
  }

  /**
   * Send user feedback about Product to backend.
   */
  function sendFeedback() {
    const feedback = getFeedbackData();

    server.sendFeedback(feedback)
      .then(() => mediator.publish('onFeedbackSave'));
  }

  /**
   * Send Feedback id on server to delete it from DB.
   */
  function deleteFeedback() {
    const $element = $(this);
    const id = $element.data('id');

    server.deleteFeedback(id)
      .then(() => mediator.publish('onFeedbackDelete', $element));
  }

  function getFeedbackData() {
    const getFormFieldValue = item => DOM.$feedbackModal.find(`${DOM.field}[name="${item}"]`).val();

    const feedback = {
      id: productId,
      rating: DOM.$ratingList.find(`.${DOM.filledRatingIcon}`).size(),
    };

    const fields = ['name', 'dignities', 'limitations', 'general'];
    fields.forEach((item) => {
      feedback[item] = getFormFieldValue(item);
    });

    return feedback;
  }

  function changeRateIcons(_, event) {
    $(event.target)
    // change class for target
      .removeClass(DOM.emptyRatingIcon)
      .addClass(DOM.filledRatingIcon)
      // change class for previous siblings of target
      .prevAll()
      .removeClass(DOM.emptyRatingIcon)
      .addClass(DOM.filledRatingIcon)
      // change class for next siblings of target
      .end()
      .nextAll()
      .removeClass(DOM.filledRatingIcon)
      .addClass(DOM.emptyRatingIcon);
  }

  function setBtnActiveState() {
    DOM.$feedbackBtn.prop('disabled', false);
  }

  function feedbackSavedResponse() {
    DOM.$feedbackBtn.addClass('hidden');
    DOM.$closeModalBtn.removeClass('hidden');
    DOM.$successModalText
      .removeClass('hidden')
      .siblings().addClass('hidden');
  }

  function feedbackDeleteResponse(_, element) {
    $(element).parent().fadeOut('fast');
  }

  function filterByRating() {
    const rating = $(this).data('rating');

    DOM.$feedbackList
      .find(`div[data-rating="${rating}"]`)
      .fadeToggle('fast');
  }

  function truncateDescription() {
    const $this = $(this);

    if ($this.hasClass('less')) {
      $this.removeClass('less');
      $this.html('Больше');
    } else {
      $this.addClass('less');
      $this.html('Меньше');
    }

    $this.prev().fadeToggle('fast');
    $this.prev().prev().toggle();

    return false;
  }

  init();
})();
