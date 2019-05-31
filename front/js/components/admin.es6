const customColModels = [
  {
    name: 'in_pack',
    // @todo #858:15m Localize Product.in_pack field
    label: 'in pack',
    editable: true,
    editoptions: {
      type: 'number',
      step: '1',
      min: '0',
      pattern: '[0-9]',
    },
    editrules: {
      minValue: 1,
      number: true,
    },
    formatter: 'integer',
    sorttype: 'integer',
    width: 30,
  },
  {
    name: 'wholesale_small',
    label: 'мелкий опт',
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
    label: 'средний опт',
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
    label: 'крупный опт',
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
];

class SETableEditor extends TableEditor {  // Ignore ESLintBear (no-undef)
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
      'vendor_code',
      'wholesale_small',
      'wholesale_medium',
      'wholesale_large',
    ];
  }
}

new AdminCommonPlugins();  // Ignore ESLintBear (no-undef)
new AdminSidebar();  // Ignore ESLintBear (no-undef)
const seColModel = new TableEditorColModel(customColModels);  // Ignore ESLintBear (no-undef)
new SETableEditor(seColModel);
