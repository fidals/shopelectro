const jQgridSettings = (() => {
  /**
   * jQgrid colModel Options.
   * @link http://goo.gl/MH03xr
   */
  const colModel = [
    {
      name: 'id',
      label: 'ID',
      key: true,
      sorttype: 'integer',
      width: 30,
    },
    {
      name: 'name',
      label: 'Название',
      editable: true,
      editrules: {
        required: true,
      },
      width: 200,
    },
    {
      name: 'title',
      label: 'Заголовок',
      editable: true,
      editrules: {
        required: true,
      },
      width: 200,
    },
    {
      name: 'category_name',
      label: 'Категория',
      editable: true,
      editoptions: {
        dataInit(elem) {
          autocompleteInit(elem);
        },
      },
      width: 150,
    },
    {
      name: 'category_id',
      hidden: true,
    },
    {
      name: 'price',
      label: 'Цена',
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
      sorttype: 'integer',
      width: 50,
    },
    {
      name: 'purchase_price',
      label: 'Закупочная цена',
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
      sorttype: 'integer',
      width: 50,
    },
    {
      name: 'in_stock',
      label: 'Наличие',
      editable: true,
      editoptions: {
        type: 'number',
        step: '1',
        min: '0',
        pattern: '[0-9]',
      },
      editrules: {
        minValue: 0,
        required: true,
        number: true,
      },
      formatter: 'integer',
      sorttype: 'integer',
      width: 40,
    },
    {
      name: 'is_active',
      label: 'Активность',
      align: 'center',
      editable: true,
      editoptions: { value: '1:0' },
      edittype: 'checkbox',
      formatter: 'checkbox',
      width: 44,
    },
    {
      name: 'is_popular',
      label: 'Топ',
      align: 'center',
      editable: true,
      editoptions: { value: '1:0' },
      edittype: 'checkbox',
      formatter: 'checkbox',
      width: 42,
    },
    {
      label: '<div class="text-center"><i class="fa fa-2x fa-trash-o"</i></div>',
      align: 'center',
      formatter: 'removeTag',
      sortable: false,
      width: 30,
    },
  ];

  /**
   * Init jQuery autocomplete for category cell.
   */
  function autocompleteInit(el) {
    $(el).autocomplete({
      source(request, response) {
        $.ajax({
          type: 'GET',
          url: '/admin/autocomplete/',
          data: {
            term: request.term,
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

  /**
   * Return checked filters field names.
   */
  const getFieldNames = $checkboxes => $checkboxes.map(item => item.replace('filter-', ''));

  /**
   * Get jQgrid settings from localStorage or default.
   */
  function getSettings() {
    const storedFilters = admin.getStoredFilterKey();
    const fieldNames = storedFilters ? getCustomFieldNames(storedFilters) : getStandardFieldNames();

    return generateSettings(fieldNames);
  }

  function getCustomFieldNames(storedFilters) {
    return getFieldNames(JSON.parse(storedFilters));
  }

  function getStandardFieldNames() {
    const checkboxIds = [];
    const $checkboxes = admin.getCheckedCheckboxes();
    $.each($checkboxes, (_, item) => checkboxIds.push($(item).attr('id')));

    return getFieldNames(checkboxIds);
  }

  /**
   * Generate settings from colModel object.
   * @param fieldNames - filter checked names
   */
  function generateSettings(fieldNames) {
    const allSettings = jQgridSettings.colModel;
    const generatedSettings = [];

    for (const field of fieldNames) {
      for (const item of allSettings) {
        if (item.name === field) {
          generatedSettings.push(item);
        }
      }
    }

    generatedSettings.unshift(allSettings[0]);
    generatedSettings.push(allSettings[allSettings.length - 1]);

    return generatedSettings;
  }

  return {
    colModel,
    getSettings,
  };
})();
