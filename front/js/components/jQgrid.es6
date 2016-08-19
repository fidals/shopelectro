const jQgridComponent = (() => {
  const jQgrid = {
    $: $('#jqGrid'),
    $editAllBtn: $('#edit-all-mode'),
    $saveRowsBtn: $('#save-rows'),
    $searchField: $('#search-field'),
    autocompleteUrl: '/admin/autocomplete/',
    entityId: 0,
    selectedRowData: {},
    clientSettings: [
      {
        label: 'ID',
        name: 'id',
        key: true,
        width: 30,
        sorttype: 'integer',
      },
      {
        label: 'Name',
        name: 'name',
        width: 250,
        editable: true,
      },
      {
        name: 'category_id',
        hidden: true,
      },
      {
        label: 'Category',
        name: 'category_name',
        width: 150,
        editable: true,
        editoptions: {
          dataInit(el) {
            // Инициализируем jQuery autocomplete.
            $(el).autocomplete({
              source(request, response) {
                $.ajax({
                  type: 'GET',
                  url: jQgrid.autocompleteUrl,
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
              select(_, ui) {
                // Подставляем надпись в поле ввода
                $(el).val(ui.item.label);

                return false;
              },
            });

            $(el).on('keydown', event => {
              if (event.which === 13) {
                event.preventDefault();
                setTimeout(() => saveCurrentRow(), 500);
              }
            });
          },
        },
      },
      {
        label: 'Price',
        name: 'price',
        width: 50,
        editable: true,
        editrules: {
          minValue: 0,
          required: true,
        },
        sorttype: 'integer',
        formatter: 'currencyFmatter',
      },
      {
        label: 'In stock',
        width: 50,
        align: 'center',
        formatter: 'checkbox',
        editable: true,
      },
      {
        label: 'Is popular',
        width: 50,
        align: 'center',
        formatter: 'checkbox',
        editable: true,
      },
      {
        label: 'Remove',
        width: 50,
        align: 'center',
        formatter: 'removeTag',
      },
    ],
  };

  const MODAL = {
    $: $('#confirm-modal'),
    $removeBtn: $('.js-modal-delete'),
    $cancelBtn: $('.js-modal-delete-cancel'),
    $forEntityName: $('#entity-to-remove'),
    deleteClass: 'js-confirm-delete-modal',
  };

  const selectedData = {
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
    $(document).on('click', `.${MODAL.deleteClass}`, showConfirmModal);
    jQgrid.$editAllBtn.click(startEdit);
    jQgrid.$saveRowsBtn.click(saveRows);
    jQgrid.$searchField.on('keyup', searchInTable);
    MODAL.$removeBtn.click(submitConfirmModal);
    MODAL.$cancelBtn.click(closeConfirmModal);
  }

  /**
   * Extend jQgrid formatter.
   * Add currency sign for price text value on render.
   * @link http://www.trirand.com/jqgridwiki/doku.php?id=wiki:custom_formatter
   */
  $.extend($.fn.fmatter, {
    currencyFormatter: cellValue => `$${cellValue}`,
  });

  /**
   * Remove currency sign for price text value in edit mode.
   */
  $.extend($.fn.fmatter.currencyFormatter, {
    unformat: cellValue => cellValue.replace('$', ''),
  });

  /**
   * Render html for entity removing.
   */
  $.extend($.fn.fmatter, {
    removeTag(_, options) {
      return `
        <div class="jqgrid-remove-icon ${MODAL.deleteClass} glyphicon glyphicon-trash"
             title="Удалить запись" data-id="${options.rowId}" data-toggle="modal"
             data-target="#remove-modal">
        </div>
      `;
    },
  });

  /**
   * Init jQgrid with settings came from server.
   */
  function jQgridInit() {
    jQgrid.$.jqGrid({
      url: '/admin/generate-table-data',
      // editurl: '/admin/edit/',
      editurl: 'clientArray',
      styleUI: 'Bootstrap',
      altRows: true,
      altclass: 'jqgrid-secondary',
      autoencode: true,
      datatype: 'json',
      colModel: jQgrid.clientSettings,
      loadonce: true,
      viewrecords: true,
      width: 1400,
      height: 480,
      rowNum: 30,
      pager: '#jqGridPager',
      beforeSelectRow: beforeSelect,
      onSelectRow: editRow,
      onCellSelect: collectCellData,
      loadComplete: filterTableByUrlSearchParam,
    });
  }

  /**
   * Collect row data before row selecting if row is not in edit mode.
   * @param rowId - id of jQgrid row;
   */
  function beforeSelect(rowId) {
    const $parentRow = $(event.target).closest('.jqgrow');
    const isInEditMode = !!($parentRow.find('.inline-edit-cell').size());

    if (!isInEditMode) {
      jQgrid.selectedRowData = getRowData(rowId);
    }
  }

  /**
   * Edit selected row.
   * `lastSelectedRowId` is need for resetting edit mode for previous row.
   * @param rowId - id of jQgrid row;
   */
  let lastSelectedRowId;

  function editRow(rowId) {
    jQgrid.$.jqGrid('restoreRow', lastSelectedRowId);

    jQgrid.$.jqGrid('editRow', rowId, {
      keys: true,
      focusField: selectedData.cellIndex,
    });

    lastSelectedRowId = rowId;
  }

  const getRowData = rowId => jQgrid.$.getRowData(rowId);

  const getRowsDataByCategoryId = categoryId =>
    jQgrid.$.getGridParam('data').filter(cell => cell.category_id === Number(categoryId));

  /**
   * Get request's value from request's body
   * @param key - request's key
   */
  const getSearchValue = (key) => {
    const searchBodyPair = decodeURIComponent(document.location.search).slice(1).split('&');
    const splitedPair = searchBodyPair.map(item => item.split('='));
    const [[_, searchValue]] = splitedPair.filter(item => {
      const [searchKey, _] = item;
      return searchKey === key;
    });
    return searchValue;
  };

  const insertValueToFilterField = value => {
    $(jQgrid.$searchField).val(value);
    searchInTable();
  };

  const hasUrlSearchKey = requestKey =>
    document.location.search.indexOf(requestKey) !== -1;

  function filterTableByUrlSearchParam() {
    const jsTreeSearchKey = 'category_id';
    if (hasUrlSearchKey(jsTreeSearchKey)) {
      const categoryId = getSearchValue(jsTreeSearchKey);
      const rowsData = getRowsDataByCategoryId(categoryId);
      if (rowsData) {
        insertValueToFilterField(rowsData[0]['category_name']);
      }
    }
  }

  /**
   * Get cell data by row id.
   * @param rowId - id of jQgrid row;
   * @param cellIndex - cell index of selected row;
   */
  function collectCellData(rowId, cellIndex) {
    selectedData.id = rowId;
    selectedData.cellIndex = cellIndex;
    selectedData.fullData = getRowData(rowId);
  }

  /**
   * Filter table data by live search on client side.
   */
  function searchInTable() {
    const searchText = jQgrid.$searchField.val();

    const filter = {
      groupOp: 'OR',
      rules: [{
        field: 'OrderID',
        op: 'cn',
        data: searchText,
      }, {
        field: 'CustomerID',
        op: 'cn',
        data: searchText,
      }, {
        field: 'Freight',
        op: 'cn',
        data: searchText,
      }, {
        field: 'ShipName',
        op: 'cn',
        data: searchText,
      }],
    };

    jQgrid.$[0].p.search = filter.rules.length > 0;
    $.extend(jQgrid.$[0].p.postData, {
      filters: JSON.stringify(filter),
    });

    jQgrid.$.trigger('reloadGrid', [{ page: 1 }]);
  }

  /**
   * Edit all mode and saving grid data.
   */
  const getJqGridIds = () => jQgrid.$.jqGrid('getDataIDs');

  function startEdit() {
    const ids = getJqGridIds();

    for (let i = ids.length; i >= 0; i--) {
      jQgrid.$.jqGrid('editRow', ids[i]);
    }
  }

  function saveRows() {
    const ids = getJqGridIds();

    for (let i = 0; i < ids.length; i++) {
      jQgrid.$.jqGrid('saveRow', ids[i]);
    }
  }

  /**
   * Confirm remove entity modal methods.
   */
  function showConfirmModal() {
    jQgrid.entityId = $(event.target).attr('data-id');
    // TODO: CustomerID will be replaced by entity name.
    MODAL.$forEntityName.text(jQgrid.selectedRowData.CustomerID);
    MODAL.$.addClass('modal-show');
  }

  function submitConfirmModal() {
    // TODO: We need to make Ajax request with id of entity to remove.
    alert(`Product's id to delete is ${jQgrid.entityId}`);
    jQgrid.$.jqGrid('delRowData', selectedData.id);
    closeConfirmModal();
  }

  function closeConfirmModal() {
    MODAL.$.removeClass('modal-show');
  }

  /**
   * Save row manually.
   */
  function saveCurrentRow() {
    console.log('Was');
    console.log(jQgrid.selectedRowData);
    console.log('Came');
    console.log(getRowData(jQgrid.selectedRowData.id));
    // jQgrid.$.saveRow(jQgrid.selectedRowData.id);
  }

  init();
})();
