const helpers = (() => {
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
    const paramName = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp(`[\\?&]${paramName}=([^&#]*)`);
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  }

  /**
   * Remove only given url query param.
   *
   * @param {string} param
   */
  function removeQueryParam(param) {
    const regex = new RegExp(`(\\?|&)${param}=(\\d|,)*`);
    return window.location.href.replace(regex, '');
  }

  return {
    getUrlParam,
    isPhoneValid,
    isEmailValid,
    removeQueryParam,
    setDisabledState,
  };
})();
