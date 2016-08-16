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
    initializeSlimScroll();
  }

  function setUpListeners() {
    DOM.$sidebarToggle.click(toggleSidebar);
    DOM.$sidebarTree.bind('state_ready.jstree',
      () => DOM.$sidebarTree.bind('select_node.jstree', redirectToEditePage));
    $(window).on('resize orientationChange', initializeSlimScroll);
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
        'plugins': ['contextmenu', 'state'],
        'contextmenu': {
          'items': {
            'to-site-page': {
              'separator_before': false,
              'separator_after': false,
              'label': 'Table Editor',
              'icon': 'fa fa-columns',
              'action': data => {
                window.location.assign('/admin/editor/?category_id=' + $(data.reference[0]).attr('category_id'));
              },
            },
            'to-tableEditor': {
              'separator_before': false,
              'separator_after': false,
              'label': 'На страницу',
              'icon': 'fa fa-link',
              'action': data => {
                window.location.assign($(data.reference[0]).attr('href_site_page'));
              },
            },
          },
        },
      });
  }

  function redirectToEditePage(e, data) {
    if (data.event.which === 1) {
      const path = $(data.event.target).attr('href_admin_page');
      if (path !== window.location.pathname) {
        window.location.assign(path);
      }
    }
  }

  /**
   * setup SlimScroll pligin
   */
  function initializeSlimScroll() {
    DOM.$sidebarTree.slimScroll({
      destroy: true,
    });
    const size_ = $(window).height() - (2 * $('.admin-header-wrapper').height()) -
      $('#sidebar-links').height();
    DOM.$sidebarTree.slimScroll({
      height: size_ + 'px',
    });
  }

  init();
})();
