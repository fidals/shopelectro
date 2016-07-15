const validator = (() => {
  const CONFIG = {
    regexpPhone: /(\+\d\s|\+\d)\(?\d{3}(\)|\)\s)?-?\d{1}-?\d{1}-?(\d{1}|\d{1}\s)-?\d{1}-?(\d{1}|\d{1}\s)-?\d{1}-?\d{1}/g,
    regexpEmail: /^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,}$/,
  };

  /**
   * Returns boolean result of phone number validation.
   * Phone number should consist of 11 numbers. Number could have whitespaces.
   *
   * @param data - phone number
   */
  const isPhoneValid = data => CONFIG.regexpPhone.test(data);

  /**
   * Returns boolean result of email validation.
   *
   * @param data - email
   */
  const isEmailValid = data => CONFIG.regexpEmail.test(data.toLowerCase());

  return {
    isPhoneValid,
    isEmailValid,
  };
})();
