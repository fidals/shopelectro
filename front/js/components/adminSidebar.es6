(() => {
  const DOM = {
    $sidebarToggle: $('.js-toggle-sidebar'),
    $header: $('.js-admin-header-wrapper'),
    $sidebarTree: $('#js-tree'),
    $sidebarLinks: $('#sidebar-links'),
  };

  const config = {
    sidebarStateKey: 'hiddenAdminSidebar',
    getTreeItemsUrl: '/admin/get-tree-items/',
    tableEditorPageUrl: '/admin/editor/?search_term=',
    scrollMagicRatio: 1.75,
  };

  const init = () => {
    setSidebarState();
    pluginsInit();
    setUpListeners();
  };

  function pluginsInit() {
    jsTreeInit();
    slimScrollInit();
  }

  function setUpListeners() {
    DOM.$sidebarToggle.click(toggleSidebar);
    DOM.$sidebarTree.bind('state_ready.jstree',
      () => DOM.$sidebarTree.bind('select_node.jstree', redirectToEditPage));
    $(window).on('resize orientationChange', slimScrollReInit);
  }

  /**
   * Set sidebar state depending on stored key.
   */
  function setSidebarState() {
    if (isSidebarClosed()) {
      $('body').toggleClass('collapsed');
    }
  }

  /**
   * Check sidebar stored state.
   */
  function isSidebarClosed() {
    return localStorage.getItem(config.sidebarStateKey) === '1';
  }

  /**
   * Toggle admin sidebar & store it's state.
   */
  function toggleSidebar() {
    $('body').toggleClass('collapsed');
    localStorage.setItem(config.sidebarStateKey, isSidebarClosed() ? 0 : 1);
  }

  /**
   * Setup jsTree plugin
   */
  function jsTreeInit() {
    DOM.$sidebarTree
      .jstree({
        core: {
          data: {
            url: config.getTreeItemsUrl,
            dataType: 'json',
            data(node) {
              return node.id === '#' ? false : { id: node.id };
            },
          },
          check_callback: true,
        },
        plugins: ['contextmenu', 'state'],
        contextmenu: {
          items: {
            'to-tableEditor': {
              separator_before: false,
              separator_after: false,
              label: 'Table Editor',
              icon: 'fa fa-columns',
              action: data => {
                window.location.assign(config.tableEditorPageUrl +
                  $(data.reference[0]).attr('search-term'));
              },
              _disabled(obj) {
                const $referenceParent = $(obj.reference).parent();
                return !($referenceParent.hasClass('jstree-leaf') ||
                         $referenceParent.find('ul:first').find('li:first')
                         .hasClass('jstree-leaf'));
              },
            },
            'to-site-page': {
              separator_before: false,
              separator_after: false,
              label: 'На страницу',
              icon: 'fa fa-link',
              action: data => {
                window.location.assign($(data.reference[0]).attr('href-site-page'));
              },
            },
          },
        },
      });
  }

  function redirectToEditPage(_, data) {
    if (data.event.which === 1) {
      const path = $(data.event.target).attr('href-admin-page');
      if (path !== window.location.pathname) {
        window.location.assign(path);
      }
    }
  }

  /**
   * Setup SlimScroll plugin.
   */
  function slimScrollReInit() {
    DOM.$sidebarTree.slimScroll({
      destroy: true,
    });

    slimScrollInit();
  }

  function slimScrollInit() {
    const scrollHeight = $(window).outerHeight() -
      (config.scrollMagicRatio * DOM.$header.outerHeight()) - DOM.$sidebarLinks.outerHeight();

    DOM.$sidebarTree.slimScroll({
      height: `${scrollHeight}px`,
    });
  }

  init();
})();
