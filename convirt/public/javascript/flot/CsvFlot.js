/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, 2008-2009
 */

/**
 * @class Ext.ux.CsvFlot
 * @extends Ext.ux.Flot
 * Flot for display CSV data
 *<br><br>
 * typeof data 
 * <li>String:
 *  CsvFlot uses the data as CSV string which is not parsed.
 *  And it parse the string.
 *  After parsing, CsvFlot uses the data as array.
 * </li>
 *
 * <li>Array
 *  CsvFlot uses the data as Array that is already parsed.
<pre>
[[0, 1, 2, 3], [4, 5, 6], [7, 8, 9],...]
</pre>
 * </li>
 *
 * <li>Object
 *  object which includes CSV data and series options.
 *  The following members are used instead of this contains.
 *   <ul>
 *   <li>header</li>
 *   <li>xColumn</li>
 *   <li>type</li>
 *   <li>sortType</li>
 *   <li>data</li>
 *   </ul>
 * </li>
 */
Ext.ux.CsvFlot = Ext.extend(Ext.ux.Flot, {
  /**
   * @cfg {String/Array/Object} data
   * See Ext.ux.CsvFlot description
   */
  /**
   * @cfg {Bool/String/Array} header
   * Header line which defines series
   * <li>true: The 1st line([0]) of data is header</li>
   * <li>String: Use as CSV string before parsing and get 1st line from</li>
   * <li>Array: Specify header array directly</li>
   */
  header: true,
  /**
   * @cfg {Number} xColumn column as x axis
   * Specify it by member name of header or index of columns
   */
  xColumn: 0,

  // private
  initComponent: function() {
    Ext.ux.CsvFlot.superclass.initComponent.call(this);
  },

  // private
  setupData: function(data, series) {
    var header   = this.header;
    var xColumn  = this.xColumn;
    var type     = this.type;
    var sortType = this.sortType;
    if (!data || typeof data.length == 'undefined') {
      header   = data.header   || header;
      xColumn  = data.xColumn  || xColumn;
      type     = data.type     || type;
      sortType = data.sortType || sortType;
      data     = data.data;
    }
    if (typeof data == 'string') { data = Csv.parse(data); }
    var i, len, j, dlen, slen, idx;

    // If there is no the series, the 1st line is CSV header.
    if (typeof header == 'boolean') {
      if (header) {header = data.shift();}
    } else if (typeof header == 'string') {
      header = Csv.parse(header)[0];
    }

    // TODO Create Ext.ux.data.CsvReader
    var store = new Ext.data.JsonStore({});
    var store_data = [], fields = [];
    for (i = 0, len = header.length; i < len; i++) {
      fields.push({
        name: header[i],
        type: type,
        sortType: sortType
      });
    }
    for (i = 0, len = data.length; i < len; i++) {
      var d = {};
      for (j = 0, dlen = data[i].length; j < dlen; j++) {
        idx = header[j] || j;
        d[idx] = data[i][j];
      }
      store_data.push(d);
    }
    store.loadData({
      metaData: {
        root: 'data',
        totalProperty: 'total',
        successProperty: 'success',
        fields: fields
      },
      data:  store_data,
      total: store_data.length,
      success: true
    });
    store.sort(xColumn, 'ASC');

    // Convert to Flot series 
    var _series = this.createSeries(store, xColumn);
    if (!series) {
      series = _series;
    } else {
      for (i = 0, len = series.length; i < len; i++) {
        for (j = 0, slen = _series.length; j < slen; j++) {
          idx = series[i].dataIndex || series[i].label;
          if (idx == _series[j].dataIndex) {
            series[i].data = _series[j].data;
            break;
          }
        }
      }
    }
    this.header  = header;
    this.xColumn = xColumn;
    //this.data    = data;
    return series;
  }
});
Ext.reg('csvflot', Ext.ux.CsvFlot);
