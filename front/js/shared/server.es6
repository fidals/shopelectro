const SEND_BACKCALL = (data) => {
  return new Promise((resolve, reject) => {
    if (data.time === 'днём') {
      resolve('Днём');
    } else {
      reject('Не днём');
    }
  });
};

const fetchProducts = (url) => fetch(url).then((response) => response.text());

const sendViewType = (event, viewType) => {
  $.post('/set-view-type/', { csrfmiddlewaretoken: Cookies.get('csrftoken'), view_type: viewType });
};
