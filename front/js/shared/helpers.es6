/**
 * Function for getting cookie by a given name.
 * https://docs.djangoproject.com/en/1.9/ref/csrf/#ajax
 * @param name
 * @returns {*}
 */
let getCookie = (name) => {
    let cookieValue = null;
    let cookieString = document.cookie;
    if (cookieString && cookieString != '') {
        let cookies = cookieString.split(';');
        for (let c of cookies) {
            let cookie = $.trim(c);
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};