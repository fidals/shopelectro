const SEND_CALLBACK = (data) => {
  return new Promise((resolve, reject) => {
    if (data.time === 'днём') {
      resolve('Днём');
    } else {
      reject('Не днём');
    }
  });
}
