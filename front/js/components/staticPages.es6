{
  const DOM = {
    $fancybox: $('.fancybox'),
  };

  const init = () => {
    fancyboxInit();
  };

  function fancyboxInit() {
    if (DOM.$fancybox.size() < 0) return;

    DOM.$fancybox.fancybox(configs.plugins.fancybox);
  }

  init();
}
