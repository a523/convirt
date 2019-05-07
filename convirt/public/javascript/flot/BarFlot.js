/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, December 2008
 */

/**
 * @class Ext.ux.BarFlot
 * @extends Ext.ux.Flot
 * Flot for bar chart
 *<br><br>
 * BarFlot can accept multiple series data which is grouped by value.
<pre>
data: [{
  name:  <String>,
  label: <String>,
  total: <Number>,
  rect:  <Number>,
  xtrap: <Number>,
  ytrap: <Number>
},{
...
}]
</pre>
 *
 * 'data' requires 'name' or 'label'.
 * It becomes tick on the x axis
 * 
<pre>
series: [
 { name: 'total', label: 'Total',        dataIndex: 0 },
 { name: 'rect',  label: 'Rectangles',   dataIndex: 1 },
 { name: 'xtrap', label: 'X-Trapezoids', dataIndex: 2 },
 { name: 'ytrap', label: 'Y-Trapezoids', dataIndex: 3 },
],
</pre>
 * 
 * 'dataIndex' is required in the series configuration.
 * It is the order of bars.
 * If you don't specify it, BarFlot use index of series array.
 */
Ext.ux.BarFlot = Ext.extend(Ext.ux.Flot, {
  /**
   * @cfg {Array} data
   * please see BarFlot top
   */
  /**
   * @cfg {Object} baseSeries
   */
  baseSeries: {bars:{ show: true, align: 'center' }},

  /**
   * @cfg {Array} data
   */
  data: [],

  /**
   * @cfg {Bool/String/Object} tooltip
<pre>
<div id="{tipId}">{label}={1}</div>
</pre>
   */
  tooltip: '<div id="{tipId}">{label}={1}</div>',

  // private
  initComponent: function() {
    if (this.data) { this.setupFlotOptions(this.data); }
    Ext.ux.BarFlot.superclass.initComponent.call(this);
  },

  /**
   * reset series before redraw.
   * Usually this method is called to recycle the series.
   * @param {Array} series series to reset
   * @returns {Array} series that is reset
   */
  resetSeries: function(series) {
    var axes = ['xaxis', 'x2axis', 'yaxis', 'y2axis'];
    for (var i = 0; i < series.length; i++) {
      s = series[i];
      // clear axes
      for (var key in axes) {
        var axis = axes[key];
        if (s[axis]) {
          delete s[axis].datamax;
          delete s[axis].datamin;
          delete s[axis].ticks;
        }
      }
      // Fix for empty series
      if (s.data && typeof s.data.remove != 'function') {
        Ext.applyIf(s, s.data);
        delete s.data;
      }
      s.data = [];
    }
    return series;
  },

  // private
  setupData: function(data, series) {
    series = this.resetSeries(series);

    // determine bar width
    var bw = 1.0 / series.length * 0.6;
    var center = series.length / 2;
    this.baseSeries.bars.barWidth = bw;

    // set data to series
    for (var i = 0; i < data.length; i++) {
      var d = data[i], _d = [], key;
      for (key in d) {
        for (var j = 0; j < series.length; j++) {
          var s = series[j];
          if (s.name == key) {
            var idx = series[j].dataIndex;
            if (typeof idx == 'undefined') { idx = j; }
            var pos = i + bw * (idx - center + 0.5);
            s.data = s.data || [];
            s.data.push([pos, d[key]]);
          }
          s.label = s.label || d.label || d.name || d.dataIndex;
        }
      }
    }

    return series;
  },

  // private
  setupFlotOptions: function(data) {
    this.data = data;
    var xticks = [];
    for (var i = 0, len = data.length; i < len; i++) {
      var d = data[i];
      xticks.push([i, d.label || d.name || d.dataIndex]);
    }
    this.xaxis = this.xaxis || {};
    Ext.apply(this.xaxis, {
      ticks: xticks,
      min: -0.5,
      max: i-0.5
    });
    this.yaxis = this.yaxis || {};
    Ext.apply(this.yaxis, {
      ticks: 10,
      min: 0
      //max: ????
    });
  },

  /**
   * update current series data to new one
   * @param {Array} data 
   */
  updateData: function(data) {
    var series = this.getData();
    series = this.setupData(data, series);
    this.setupFlotOptions(data);
    Ext.ux.BarFlot.superclass.plot.call(this, series);
  }
});
Ext.reg('barflot', Ext.ux.BarFlot);

