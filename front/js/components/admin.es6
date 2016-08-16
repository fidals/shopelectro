const admin = (() => {
  const DOM = {
    $productPage: $('.model-product'),
    $removeIcon: $('.js-remove-image'),
    $imageItem: $('.js-list-item'),
    searchFieldId: '#searchbar',
  };

  const config = {
    removeUrl: '/admin/remove-image/',
    completeURL: '/admin/autocomplete/',
    minChars: 3,
  };

  const jQgrid = {
    $: $('#jqGrid'),
    $editAllBtn: $('#edit-all-mode'),
    $saveRowsBtn: $('#save-rows'),
    $searchField: $('#search-field'),
    clientSettings: [
      {
        label: 'ID',
        name: 'OrderID',
        key: true,
        width: 30,
        sorttype: 'integer',
      },
      {
        label: 'Customer ID',
        name: 'CustomerID',
        width: 150,
        editable: true,
      },
      {
        label: 'Order Date',
        name: 'OrderDate',
        width: 150,
        formatter: 'date',
        newformat: 'd-m-Y',
      },
      {
        label: 'Freight',
        name: 'Freight',
        width: 100,
        editable: true,
        editrules: {
          minValue: 0,
          required: true,
        },
        sorttype: 'integer',
        formatter: 'currencyFmatter',
      },
      {
        label: 'Ship Name',
        name: 'ShipName',
        width: 150,
        editable: true,
      },
      {
        name: 'CheckBox',
        width: 100,
        align: 'center',
        formatter: 'checkbox',
        editable: true,
      },
      {
        label: 'Remove',
        name: 'remove',
        width: 100,
        align: 'center',
        formatter: 'removeTag',
      },
    ],
    dataURL:
    'https://gist.githubusercontent.com/YozhEzhi/' +
    '2d6ad664d8b9e1c98f4958cc13bd17a0/raw/' +
    'e80143205a27570a45672fe5e6563d331c965a1f/' +
    'jq_test_data.json',
    entityId: 0,
    selectedRowData: {},
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
    autoCompleteInit();
    jQgridInit();
  }

  function setUpListeners() {
    $(document).on('click', `.${MODAL.deleteClass}`, showConfirmModal);
    DOM.$removeIcon.click(removeImage);
    jQgrid.$editAllBtn.click(startEdit);
    jQgrid.$saveRowsBtn.click(saveRows);
    jQgrid.$searchField.on('keyup', searchInTable);
    MODAL.$removeBtn.click(submitConfirmModal);
    MODAL.$cancelBtn.click(closeConfirmModal);
    $(document).ready(() => {
      const id = decodeURIComponent(window.location.search).split('=')[1];
    });
  }

  function autoCompleteInit() {
    return new autoComplete({
      selector: DOM.searchFieldId,
      minChars: config.minChars,
      source: (term, response) => {
        $.getJSON(config.completeURL, {
          q: term,
          pageType: getCurrentPageType(),
        }, namesArray => {
          response(namesArray);
        });
      },
    });
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
   * Render `removeTag` string as formatter that returns html for entity removing.
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
      url: jQgrid.dataURL,
      editurl: '/admin/edit/',
      styleUI: 'Bootstrap',
      altRows: true,
      altclass: 'jqgrid-secondary',
      autoencode: true,
      datatype: 'json',
      colModel: jQgrid.clientSettings,
      loadonce: true,
      viewrecords: true,
      width: 1170,
      height: 480,
      rowNum: 30,
      pager: '#jqGridPager',
      beforeSelectRow: beforeSelect,
      onSelectRow: editRow,
      onCellSelect: getCellData,
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
   * `lastSelection` is needed for resetting edit mode by clicking on other row\cell.
   * @param rowId - id of jQgrid row;
   */
  let lastSelection;

  function editRow(rowId) {
    jQgrid.$.jqGrid('restoreRow', lastSelection);
    jQgrid.$.jqGrid('editRow', rowId, {
      keys: true,
      focusField: selectedData.cellIndex,
    });

    lastSelection = rowId;
  }

  /**
   * Get row data by row id.
   * @param rowId - id of jQgrid row;
   */
  const getRowData = rowId => jQgrid.$.getRowData(rowId);

  /**
   * Get cell data by row id.
   * @param rowId - id of jQgrid row;
   * @param cellIndex - cell index of selected row;
   */
  function getCellData(rowId, cellIndex) {
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
   * Return current page type.
   */
  function getCurrentPageType() {
    return (DOM.$productPage.size() > 0) ? 'product' : 'category';
  }

  /**
   * Remove entity image.
   */
  function removeImage() {
    const $target = $(event.target);

    $.post(config.removeUrl, { url: $target.data('id') })
      .success(() => $target.closest(DOM.$imageItem).slideUp());
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
  init();
})();
