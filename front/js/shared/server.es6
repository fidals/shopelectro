const SEND_BACKCALL = (data) => {
  return new Promise((resolve, reject) => {
    if (data.time === 'днём') {
      resolve('Днём');
    } else {
      reject('Не днём');
    }
  });
};

let fetchProducts = (url) => {
  return fetch(url)
    .then((response) => response.text());
};

let sendViewType = (event, viewType) => {
  let data = { 'csrfmiddlewaretoken': getCookie('csrftoken'), 'view_type': viewType };

  return fetch('/set-view-type/', {
      method: 'post',
      body: JSON.stringify(data)
    });
};

