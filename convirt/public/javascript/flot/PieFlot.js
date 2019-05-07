/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, December 2008
 */

/**
 * @class Ext.ux.PieFlot
 * @extends Ext.ux.Flot
 * The flot for pie chart
 *<br><br>
 * PieFlot can accept multiple series data which is grouped by value.
<pre>
data: [{
  label: <String>,
  data: [[<id>, <value>], ...]
},{
...
}]
</pre>
 *
 * The x value of data (data[i][j][0]) is set as the serie ID, and it is ignored internally,
 * the sum of y value (data[i][j][1]) is real value of the serie.
 *<br><br>
 * The ratio which the serie take in the pie chart is the fraction of each serie.
 *
<pre>
series: [
  { label: 'Niveau A', data: [[0,2]]},  # 40%
  { label: 'Niveau B', data: [[1,2]]},  # 40%
  { label: 'Niveau C', data: [[2,1]]},  # 20%
  { label: 'Niveau D', data: [[3,0]]}   #  0%
],
</pre>
 *
 * Note that pie chart does not require any operations, context menu contains
 * just a property menu by default.
 */
Ext.ux.PieFlot = Ext.extend(Ext.ux.Flot, {
  /**
   * @cfg {Array} colors
   * changed from Flot default
   */
  colors: ["#59bb14", "#39a5fe", "#dc5f13", "#edc240", "#afd8f8", "#9440ed"],

  /**
   * @cfg {Object} selection
   * mode is null by default
   */
  selection: { mode: null },

  /**
   * @cfg {Bool/String/Object} tooltip
   * false by default
   */
  tooltip: false,

  /**
   * @property contextMenu
   * @type Array
   * just 'property'
   */
  contextMenu: [{
    name: 'property',
    text: _('Property'),
    iconCls: 'puzzle',
    handler: function() { this.showProperty(); }
  }],

  /**
   * @property datapointContextMenu
   * @type Array 
   * disable by default
   */
  datapointContextMenu: false,

  // private
  initComponent: function() {
    Ext.ux.PieFlot.superclass.initComponent.call(this);
  },

  /**
   * Convert the data of {@link Ext.data.JsonStore} to for pie flot.
   * @param {Ext.data.Store} store data store to use
   * If you specify nothing, this.store is used.
   * @param {String} xField The field name for x-axis 
   * It is mathed the order of dataIndex, name.
   * If you specify nothing, store.xField is used.
   * @param {String} yField The field name for y-axis 
   * It is mathed the order of dataIndex, name.
   * If you specify nothing, store.yField is used.
   * @return {Array} data array which can be used by flot.
   */
  createSeries: function(store, xField, yField) {
    store = store || this.store;
    if (typeof xField == 'undefined') { xField = store.xField; }
    if (typeof yField == 'undefined') { yField = store.yField; }
    var series = [];
    store.each(function(rec) {
      this.series.push({
        label: rec.get(this.xField),
        data: [[0, rec.get(this.yField)]]
      });
    }, {series: series, xField: xField, yField: yField});
    return series;
  }
});
Ext.reg('pieflot', Ext.ux.PieFlot);

