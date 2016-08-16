const adminSidebar = (() => {
  const DOM = {
    $sidebarToggle: $('.js-toggle-sidebar'),
    $sidebarItem: $('.jstree-anchor'),
    $sidebarTree: $('#js-tree'),
  };

  const config = {
    sidebarStateKey: 'hiddenAdminSidebar',
    getTreeItemsUrl: '/admin/get-tree-items/',
  };

  const init = () => {
    setSidebarState();
    pluginsInit();
    setUpListeners();
  };

  function pluginsInit() {
    jsTreeInit();
  }

  function setUpListeners() {
    DOM.$sidebarToggle.click(toggleSidebar);
    DOM.$sidebarTree.bind('state_ready.jstree',
      () => DOM.$sidebarTree.bind('select_node.jstree', redirectToEditePage));
  }

  /**
   * Set sidebar state depending on stored key.
   */
  const isSidebarClosed = () => localStorage.getItem(config.sidebarStateKey) === '1';

  function setSidebarState() {
    if (isSidebarClosed()) {
      toggleSidebar();
    }
  }

  /**
   * Toggle admin sidebar & store it's state.
   */
  function toggleSidebar() {
    $('body').toggleClass('collapsed');
    localStorage.setItem(config.sidebarStateKey, isSidebarClosed() ? 0 : 1);
  }

  /**
   *setup jsTree plugin
   */
  function jsTreeInit() {
    DOM.$sidebarTree
      .jstree({
        'core': {
          'data': {
            'url': config.getTreeItemsUrl,
            'dataType': 'json',
            'data': function (node) {
              return node.id === '#' ? false : { 'id': node.id };
            },
          },
          'check_callback': true,
        },
        "contextmenu":{
          "items": function($node) {
            var tree = DOM.$sidebarTree.jstree(true);
            return {
              "to-site-page": {
                "separator_before": false,
                "separator_after": false,
                "label": "Table Editor",
                'icon': 'fa fa-columns',
                'action': data => {
                },
              },
              "to-tableEditor": {
                "separator_before": false,
                "separator_after": false,
                'label': 'На страницу',
                'icon': 'fa fa-link',
                'action': data =>
                  window.location.pathname = $(data.reference[0]).attr('href_site_page')
                ,
              },
            };
          },
        },
        'plugins': ['contextmenu', 'state'],
      });
  }

  function redirectToEditePage(e, data) {
    if (data.event.which === 1) {
      const pathname = $(data.event.target).attr('href_admin_page');
      if (pathname !== window.location.pathname) {
        window.location.pathname = pathname;
      }
    }
  }
  init();
})();
