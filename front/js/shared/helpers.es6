const helpers = (() => {  // Ignore ESLintBear (no-unused-vars)
  const config = {
    regexpPhone: /(\+\d\s|\+\d)\(?\d{3}(\)|\)\s)?-?\d{1}-?\d{1}-?(\d{1}|\d{1}\s)-?\d{1}-?(\d{1}|\d{1}\s)-?\d{1}-?\d{1}/g,
    regexpEmail: /^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,}$/,
    loadingText: 'Пожалуйста, подождите...',
  };

  /**
   * Returns boolean result of phone number validation.
   * Phone number should consist of 11 numbers. Number could have whitespaces.
   *
   * @param data - phone number
   */
  const isPhoneValid = data => config.regexpPhone.test(data);

  /**
   * Returns boolean result of email validation.
   *
   * @param data - email
   */
  const isEmailValid = data => config.regexpEmail.test(data.toLowerCase());

  function setDisabledState($button, loadingText = config.loadingText) {
    $button
      .attr('disabled', 'disabled')
      .text(loadingText)
      .val(loadingText);
  }

  function getUrlParam(name) {
    const paramName = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');  // Ignore ESLintBear (no-useless-escape)
    const regex = new RegExp(`[\\?&]${paramName}=([^&#]*)`);
    const results = regex.exec(window.location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  }

  function getUrlEndpointParam(name) {
    const regex = new RegExp(`\/${name}\/(.+?)\/`);  // Ignore ESLintBear (no-useless-escape)
    const results = regex.exec(location.href);
    return results === null ? '' : decodeURIComponent(results[1]);
  }

  /**
   * Remove only given url query param.
   *
   * @param {string} param
   */
  function removeQueryParam(param) {
    const regex = new RegExp(`\\?${param}=[^&#]*(?!.)|\\&${param}=[^&#]*|${param}=[^&#]*(?=.)\\&`);
    return window.location.href.replace(regex, '');
  }

  function removeUrlEndpoint(name) {
    const regex = new RegExp(`\/${name}\/(.+?)\/`);  // Ignore ESLintBear (no-useless-escape)
    return window.location.href.replace(regex, '');
  }

  /**
   * Delays `fn` execution for better UI and AJAX request performance.
   *
   * @param {function} fn
   * @param {number} delay
   */
  function debounce(fn, delay) {
    let timerId;
    return function delayed(...args) {
      clearTimeout(timerId);
      timerId = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  /**
   * Hide and show long description text.
   */
  function toggleText() {
    const $this = $(this);
    if ($this.hasClass('less')) {
      $this.removeClass('less');
      $this.html('Развернуть описание');
      $this.prev().toggle();
      $this.prev().prev().fadeToggle('fast');
    } else {
      $this.addClass('less');
      $this.html('Свернуть');
      $this.prev().prev().toggle();
      $this.prev().fadeToggle('fast');
    }

    return false;
  }

  return {
    debounce,
    getUrlParam,
    getUrlEndpointParam,
    isPhoneValid,
    isEmailValid,
    removeQueryParam,
    removeUrlEndpoint,
    setDisabledState,
    toggleText,
  };
})();
