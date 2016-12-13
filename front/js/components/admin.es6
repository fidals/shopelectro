const customColumnModels = [
  {
    name: 'wholesale_small',
    label: 'Wholesale small',
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
    name: 'wholesale_medium',
    label: 'Wholesale medium',
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
    name: 'wholesale_large',
    label: 'Wholesale large',
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
    label: 'Purchase price',
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
  }
];

class TableEditorSE extends TableEditor {
  constructor(colModel = TableEditorColumnModel(), dialogBoxes = TableEditorDialogBoxes()) {
    super(colModel, dialogBoxes);
  
    this.filterFields = [
      'name',
      'category_name',
      'price',
      'purchase_price',
    ];
  }
}

const sidebar = new AdminSideBar();
const tableEditorDialogBoxes = new TableEditorDialogBoxes();
const tableEditorFilters = new TableEditorFilters();
const tableEditorColumnModel = new TableEditorColumnModel(tableEditorFilters, customColumnModels);
new TableEditorSE(tableEditorColumnModel, tableEditorDialogBoxes);
new AdminCommonPlugins();
