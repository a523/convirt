/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, May 2009
 */


Ext.onReady(function() {

  var get_zooming_series = function(x1, x2) {
    var d = [];
    for (var i = x1; i < x2; i += (x2 - x1) / 100)
        d.push([i, Math.sin(i * Math.sin(i))]);

    return [
        { label: "sin(x sin(x))", data: d }
    ];
  };

  var win = new Ext.Window({
    title: 'Zooming',
    id: 'zooming',
    layout: 'column',
    width: 500,
    height: 450,
    items: [{
      id: 'flot-zooming-birdview',
      xtype: 'flot',
      cls: 'x-panel-body',
      width: 200,
      height: 100,
      margin: 0,
      legend: { show: false },
      lines: { show: true, lineWidth: 1 },
      points: { show: false },
      shadowSize: 0,
      xaxis: { ticks: [] },
      yaxis: { ticks: [], min: -2, max: 2 },
      grid: { color: "#999", clickable: false, hoverable: false },
      selection: { mode: "xy", action: false },
      tooltip: false,
      baseSeries: {selectable: false, clickable: false, hoverable: false},
      series: get_zooming_series(0, 3 * Math.PI),
      listeners: {
        plotselected: function(flot, event, ranges, item) {
          var main_view = Ext.getCmp('flot-zooming');
          main_view.zoom(ranges);
        }
      }
    },{
      id: 'flot-zooming',
      xtype: 'flot',
      cls: 'x-panel-body',
      height: 300,
      width: 450,
      //legend: { show: true, container: $("#overviewLegend") },
      legend: { show: true },
      lines: { show: true },
      points: { show: true },
      yaxis: { ticks: 10, min: -2, max: 2 },
      selection: { mode: "xy" },
      series: get_zooming_series(0, 3 * Math.PI)
    }]
  });
  win.show();
});
