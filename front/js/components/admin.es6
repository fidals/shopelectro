const customColModels = [
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
  },
];

class SETableEditor extends TableEditor {
  constructor(colModel) {
    super(colModel);

    this.filterFields = [
      'name',
      'category_name',
      'price',
      'purchase_price',
    ];

    this.newEntityFields = [
      'name',
      'category',
      'price',
      'wholesale_small',
      'wholesale_medium',
      'wholesale_large',
    ];
  }
}

new AdminCommonPlugins();
new AdminSidebar();
const seColModel = new TableEditorColModel(customColModels);
new SETableEditor(seColModel);
