(() => {
  const urls = {
    generate: '/admin/get-table-editor-data',
    create: '/admin/product-create/',
    update: '/admin/product-update/',
    delete: '/admin/product-delete/',
  };

  const jQgrid = {
    $: $('#jqGrid'),
    $searchField: $('#search-field'),
    wasFiltered: false,
  };

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

  const init = () => {
    pluginsInit();
    setUpListeners();
  };

  function pluginsInit() {
    jQgridInit();
  }

  function setUpListeners() {
    $(document).on('click', `.${modal.deleteClass}`, showModal);
    $(document).on('keyup', event => {
      if (event.which === 27) {
        closeModal(event);
      }
    });
    jQgrid.$searchField.on('keyup', searchInTable);
    modal.$removeBtn.click(deleteProduct);
    modal.$cancelBtn.click(closeModal);
  }

  /**
   * Extend jQgrid formatter.
   * Render html for Product removing icon.
   * @link http://goo.gl/9xcr7q
   */
  $.extend($.fn.fmatter, {
    removeTag() {
      return `
        <i class="jqgrid-remove-icon ${modal.deleteClass} fa fa-2x fa-trash-o"
          title="Удалить товар" data-toggle="modal" data-target="#remove-modal"</i>
      `;
    },
  });

  /**
   * Init jQgrid with settings came from server.
   * @link http://goo.gl/qwgGCz
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
      colModel: jQgridSettings.getSettings(),
      loadonce: true,
      viewrecords: true,
      width: 1400,
      height: 500,
      rowNum: 30,
      pager: '#jqGridPager',
      onSelectRow: editRow,
      onCellSelect: collectCellData,
      loadComplete: afterLoad,
    });
  }

  /**
   * Afterload event of jQgrid.
   * @link http://goo.gl/5WwmTm
   */
  function afterLoad() {
    filterTableBySearchQuery();
  }

  /**
   * Edit selected row.
   * @param lastSelectedRowId - need for resetting edit mode for previous row;
   * @param rowId - id of selected row;
   */
  let lastSelectedRowId;

  function editRow(rowId) {
    jQgrid.$.jqGrid('restoreRow', lastSelectedRowId);

    // Cancel method by click on delete Product icon:
    if ($(event.target).hasClass(modal.deleteClass)) return;

    jQgrid.$.jqGrid('editRow', rowId, {
      keys: true,
      focusField: lastSelectedData.cellIndex,
      aftersavefunc() {
        updateProduct();
      },
    });

    lastSelectedRowId = rowId;
  }

  function getRowData(rowId) {
    return jQgrid.$.jqGrid('getRowData', rowId);
  }

  /**
   * Collect data for selected row with cell index.
   * @param rowId;
   * @param cellIndex;
   */
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
   * Get request search value from url.
   * @param key - request's key
   */
  const getSearchValue = key => {
    const searchQuery = decodeURIComponent(document.location.search).slice(1).split('&');
    const splitedPairs = searchQuery.map(item => item.split('='));
    const [[_, searchTerm]] = splitedPairs.filter(item => item.includes(key));

    return searchTerm;
  };

  /**
   * Insert `searchTerm` in jQgrid filter field.
   * @param searchTerm - request key
   */
  const insertFilterValue = searchTerm => {
    jQgrid.$searchField
      .val(searchTerm)
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
   * We should to generate `filter.rules` cause filters for search is dynamic.
   * @link http://goo.gl/NFoUvf
   */
  function searchInTable() {
    const filterFields = [
      'name',
      'category_name',
      'price',
      'purchase_price',
    ];

    const searchText = jQgrid.$searchField.val();

    const filter = {
      groupOp: 'OR',
      rules: [{
        field: 'id',
        op: 'cn',
        data: searchText,
      }],
    };

    for (const field of filterFields) {
      if ($(`#jqGrid_${field}`).size() > 0) {
        filter.rules.push({
          field,
          op: 'cn',
          data: searchText,
        });
      }
    }

    setTimeout(() => {
      jQgrid.$[0].p.search = filter.rules.length > 0;
      $.extend(jQgrid.$[0].p.postData, {
        filters: JSON.stringify(filter),
      });

      jQgrid.$.trigger('reloadGrid', [{ page: 1 }]);
    }, 200);
  }

  /**
   * Update Product on server only if row was changed.
   */
  function updateProduct() {
    const newRowData = getRowData(lastSelectedData.id);
    const isChanged = JSON.stringify(lastSelectedData.fullData) === JSON.stringify(newRowData);

    if (!isChanged) {
      const $currentRow = $(`#${lastSelectedData.id}`);
      const offset = popover.getPopoverOffset($currentRow);

      $.post(urls.update, destructFields(newRowData))
        .success(() => {
          $currentRow.removeClass('danger');
        })
        .error(() => {
          $currentRow.addClass('danger');
          popover.showPopover(offset);
        });
    }
  }

  /**
   * Return destructured, trimmed fields from newRowData for ajax data arguments.
   */
  function destructFields(newRowData) {
    const trimmedData = {};

    for (const [key, value] of Object.entries(newRowData)) {
      trimmedData[key] = value.trim();
    }

    const {
      id,
      name,
      title,
      category_name: category_id,
      price,
      purchase_price,
      is_popular,
      is_active,
      in_stock,
    } = trimmedData;

    return {
      id,
      name,
      title,
      category_id,
      price,
      purchase_price,
      is_popular,
      is_active,
      in_stock,
    };
  }

  /**
   * Delete Product on server after modal submitting.
   * Product will be deleted after submitting modal.
   */
  function showModal(event) {
    event.stopImmediatePropagation();

    jQgrid.$.jqGrid('resetSelection');
    modal.$forProductName.text(lastSelectedData.fullData.name || 'этот товар');
    modal.$.addClass('modal-show');
  }

  function closeModal(event) {
    event.stopImmediatePropagation();
    modal.$.removeClass('modal-show');
  }

  function deleteProduct(event) {
    event.stopImmediatePropagation();

    $.post(urls.delete, {
      id: lastSelectedData.id,
    }).success(() => {
      closeModal(event);
      jQgrid.$.jqGrid('delRowData', lastSelectedData.id);
    });
  }

  init();
})();
