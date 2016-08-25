(() => {
  const urls = {
    autocomplete: '/admin/autocomplete/',
    generate: '/admin/generate-table-data',
    create: '/admin/product-create/',
    update: '/admin/product-update/',
    delete: '/admin/product-delete/',
  };

  const jQgrid = {
    $: $('#jqGrid'),
    $searchField: $('#search-field'),
    wasFiltered: false,
  };

  /**
   * jQgrid colModel Options
   * @link http://goo.gl/MH03xr
   */
  const jQgridSettings = [
    {
      key: true,
      label: 'ID',
      name: 'id',
      sorttype: 'integer',
      width: 20,
    },
    {
      editable: true,
      editrules: {
        required: true,
      },
      label: 'Название',
      name: 'name',
      width: 230,
    },
    {
      editable: true,
      editoptions: {
        dataInit(elem) {
          autocompleteInit(elem);
        },
      },
      label: 'Категория',
      name: 'category_name',
      width: 150,
    },
    {
      hidden: true,
      name: 'category_id',
    },
    {
      editable: true,
      editoptions: {
        type: 'number',
        step: '1.00',
        min: '0.00',
        pattern: '[0-9]',
      },
      editrules: {
        minValue: 0,
        required: true,
        number: true,
      },
      formatter: 'currency',
      formatoptions: {
        decimalSeparator: '.',
        thousandsSeparator: ' ',
        prefix: '₽ ',
      },
      label: 'Цена',
      name: 'price',
      sorttype: 'integer',
      width: 48,
    },
    {
      align: 'center',
      editable: true,
      editoptions: { value: '1:0' },
      edittype: 'checkbox',
      formatter: 'checkbox',
      label: 'Активность',
      name: 'page_is_active',
      width: 44,
    },
    {
      align: 'center',
      editable: true,
      editoptions: { value: '1:0' },
      edittype: 'checkbox',
      formatter: 'checkbox',
      label: 'Топ',
      name: 'is_popular',
      width: 42,
    },
    {
      align: 'center',
      formatter: 'removeTag',
      label: 'Удалить',
      sortable: false,
      width: 35,
    },
  ];

  const modal = {
    $: $('#confirm-modal'),
    $removeBtn: $('.js-modal-delete'),
    $cancelBtn: $('.js-modal-delete-cancel'),
    $forProductName: $('#product-to-remove'),
    deleteClass: 'js-confirm-delete-modal',
  };

  const lastSelectedData = {
    id: 0,
    cellIndex: 0,
    fullData: {},
  };

  /**
   * Init jQuery autocomplete for category cell.
   */
  function autocompleteInit(el) {
    $(el).autocomplete({
      source(request, response) {
        $.ajax({
          type: 'GET',
          url: urls.autocomplete,
          data: {
            q: request.term,
            pageType: 'category',
          },
          success(responseData) {
            response(responseData);
          },
          error(jqXhr, textStatus, errorThrown) {
            console.group('Autocomplete failed.');
            console.log(jqXhr);
            console.log(textStatus);
            console.log(errorThrown);
            console.groupEnd();
          },
        });
      },
      // Set autocompleted value to input.
      select(_, ui) {
        $(el).val(ui.item.label);
      },
    });
  }

  const init = () => {
    pluginsInit();
    setUpListeners();
  };

  function pluginsInit() {
    jQgridInit();
  }

  function setUpListeners() {
    $(document).on('click', `.${modal.deleteClass}`, showConfirmModal);
    $(document).on('keyup', (event) => {
      if (event.which === 27) {
        closeConfirmModal(event);
      }
    });
    jQgrid.$searchField.on('keyup', searchInTable);
    modal.$removeBtn.click(deleteProduct);
    modal.$cancelBtn.click(closeConfirmModal);
  }

  function jQgridAfterLoad() {
    filterTableBySearchQuery();
  }

  /**
   * Render html for Product removing.
   * Extend jQgrid formatter.
   * @link http://goo.gl/9xcr7q
   */
  $.extend($.fn.fmatter, {
    removeTag() {
      return `
        <div class="jqgrid-remove-icon ${modal.deleteClass} glyphicon glyphicon-trash"
             title="Удалить запись" data-toggle="modal" data-target="#remove-modal">
        </div>
      `;
    },
  });

  /**
   * Init jQgrid with settings came from server.
   * @lin http://goo.gl/qwgGCz
   */
  function jQgridInit() {
    jQgrid.$.jqGrid({
      url: urls.generate,
      editurl: 'clientArray',
      styleUI: 'Bootstrap',
      altRows: true,
      altclass: 'jqgrid-secondary',
      autoencode: true,
      datatype: 'json',
      colModel: jQgridSettings,
      loadonce: true,
      viewrecords: true,
      width: 1400,
      height: 480,
      rowNum: 30,
      pager: '#jqGridPager',
      onSelectRow: editRow,
      onCellSelect: collectCellData,
      loadComplete: jQgridAfterLoad,
    });
  }

  /**
   * Edit selected row.
   * `lastSelectedRowId` is need for resetting edit mode for previous row.
   * @param rowId - id of jQgrid row;
   */
  let lastSelectedRowId;

  function editRow(rowId) {
    jQgrid.$.jqGrid('restoreRow', lastSelectedRowId);

    // Prevent method by click on delete button:
    if ($(event.target).hasClass(modal.deleteClass)) return;

    jQgrid.$.jqGrid('editRow', rowId, {
      keys: true,
      focusField: lastSelectedData.cellIndex,
      aftersavefunc() {
        updateProduct(rowId);
      },
    });

    lastSelectedRowId = rowId;
  }

  function getRowData(rowId) {
    return jQgrid.$.jqGrid('getRowData', rowId);
  }

  function collectCellData(rowId, cellIndex) {
    const $parentRow = $(event.target).closest('.jqgrow');
    const isInEditMode = !!($parentRow.find('.inline-edit-cell').size());

    if (!isInEditMode) {
      lastSelectedData.id = rowId;
      lastSelectedData.cellIndex = cellIndex;
      lastSelectedData.fullData = getRowData(rowId);
    }
  }

  /**
   * Get request's search value from url.
   * @param key - request's key
   */
  const getSearchValue = key => {
    const searchQuery = decodeURIComponent(document.location.search).slice(1).split('&');
    const splitedPairs = searchQuery.map(item => item.split('='));
    const [[_, searchTerm]] = splitedPairs.filter(item => item.includes(key));

    return searchTerm;
  };

  const insertFilterValue = value => {
    jQgrid.$searchField
      .val(value)
      .focus()
      .trigger('keyup');

    jQgrid.wasFiltered = true;
  };

  const hasUrlSearchKey = requestKey =>
    document.location.search.indexOf(requestKey) !== -1;

  function filterTableBySearchQuery() {
    if (jQgrid.wasFiltered) return;
    const jsTreeSearchKey = 'search_term';

    if (hasUrlSearchKey(jsTreeSearchKey)) {
      const searchTerm = getSearchValue(jsTreeSearchKey);

      insertFilterValue(searchTerm);
    }
  }

  /**
   * Filter table data by live search on client side.
   * @link http://goo.gl/NFoUvf
   */
  function searchInTable() {
    const searchText = jQgrid.$searchField.val();

    setTimeout(() => {
      const filter = {
        groupOp: 'OR',
        rules: [{
          field: 'id',
          op: 'cn',
          data: searchText,
        }, {
          field: 'name',
          op: 'cn',
          data: searchText,
        }, {
          field: 'category_name',
          op: 'cn',
          data: searchText,
        }, {
          field: 'price',
          op: 'cn',
          data: searchText,
        }],
      };

      jQgrid.$[0].p.search = filter.rules.length > 0;
      $.extend(jQgrid.$[0].p.postData, {
        filters: JSON.stringify(filter),
      });

      jQgrid.$.trigger('reloadGrid', [{ page: 1 }]);
    }, 200);
  }

  /**
   * Confirm remove Product modal methods.
   */
  function showConfirmModal(event) {
    event.stopImmediatePropagation();

    jQgrid.$.jqGrid('resetSelection');
    modal.$forProductName.text(lastSelectedData.fullData.name);
    modal.$.addClass('modal-show');
  }

  function closeConfirmModal(event) {
    event.stopImmediatePropagation();
    modal.$.removeClass('modal-show');
  }

  /**
   * Update Product on server if row was changed.
   */
  function updateProduct() {
    const newRowData = getRowData(lastSelectedData.id);
    const isChanged = JSON.stringify(lastSelectedData.fullData) === JSON.stringify(newRowData);

    if (!isChanged) {
      $.post(urls.update, destructFields(newRowData))
        .success(response => {
          // TODO: Make UI feedback for user about success/fail.
          console.log(response);
        });
    }
  }

  /**
   * Return destructured fields from newRowData for ajax data argument.
   */
  function destructFields(newRowData) {
    const {
      id, name, category_name, category_id,
      price, is_popular, page_is_active,
    } = newRowData;

    return {
      id, name, category_name, category_id,
      price, is_popular, page_is_active,
    };
  }

  /**
   * Delete Product on server by modal submitting.
   */
  function deleteProduct(event) {
    event.stopImmediatePropagation();

    $.post(urls.delete, {
      id: lastSelectedData.id,
    }).success(response => {
      jQgrid.$.jqGrid('delRowData', lastSelectedData.id);
      // TODO: Make UI feedback for user about success/fail.
      console.log(response);
      closeConfirmModal(event);
    });
  }

  init();
})();
