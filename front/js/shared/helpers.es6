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

  /**
   * Disabling button prevent submit event.
   */
  const disableSubmit = $button => {
    $button
      .attr('disabled', 'disabled')
      .text(config.loadingText)
      .val(config.loadingText);
  };

  return {
    disableSubmit,
    isPhoneValid,
    isEmailValid,
  };
})();
