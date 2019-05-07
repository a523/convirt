/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, December 2008
 */

Ext.onReady(function() {
  var win = new Ext.Window({
    title: 'Horizontal Bar',
    width: 600,
    height: 480,
    layout: 'fit',
    items: [{
      xtype: 'flot',
      cls: 'x-panel-body',
      bars: {show: true, align: 'center', barWidth: 1.0, horizontal: true },
      legend: {show: true},
      tooltip: function(o) {
        var axes = this.getAxes();
        for (var i = 0; i < axes.yaxis.ticks.length; i++) {
          var tick = axes.yaxis.ticks[i];
          if (tick.v == o.datapointY) {
            return String.format("{0} : {1}%", tick.label, o.datapointX);
          }
        }
        return "";
      },
      yaxis: {
        max: 9,
        ticks: [
          [0, 'IE 6'], 
          [1, 'IE 7'], 
          [2, 'IE 8'], 
          [3, 'FF 2'],
          [4, 'FF 3'],
          [5, 'Safari'],
          [6, 'Chrome'],
          [7, 'Opera'],
          [8, 'Other Browsers']
        ]
      },
      xaxis: { max: 50 },
      series: [
        { data: [[20.46, 0]]},
        { data: [[46.77, 1]]},
        { data: [[0.82,  2]]},
        { data: [[3.77,  3]]},
        { data: [[17.18, 4]]},
        { data: [[7.93,  5]]},
        { data: [[1.04,  6]]},
        { data: [[0.71,  7]]},
        { data: [[0.0,   8]]}
      ]
    }]
  });
  win.show();
});

