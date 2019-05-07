/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, December 2008
 */

Ext.onReady(function() {
  var i, d1 = [];
  for (i = 0; i < Math.PI * 2; i += 0.25)
      d1.push([i, Math.sin(i)]);
  
  var d2 = [];
  for (i = 0; i < Math.PI * 2; i += 0.25)
      d2.push([i, Math.cos(i)]);

  var d3 = [];
  for (i = 0; i < Math.PI * 2; i += 0.1)
      d3.push([i, Math.tan(i)]);

  var series = [
    { label: "sin(x)",  data: d1},
    { label: "cos(x)",  data: d2},
    { label: "tan(x)",  data: d3}
  ];

  var win = new Ext.Window({
    title: 'Setting Options (Modified by Ext Flot Options)',
    width: 600,
    height: 480,
    layout: 'fit',
    items: [{
      xtype: 'flot',
      id: 'flot',
      cls: 'x-panel-body',
      series: series,
      lines: { show: true },
      points: { show: true },
      xaxis: {
        ticks: [0, [Math.PI * 0.5, "\u03c0/2"], [Math.PI, "\u03c0"], [Math.PI * 3 * 0.5, "3\u03c0/2"], [Math.PI * 2, "2\u03c0"]]
      },
      yaxis: {
        ticks: 10,
        min: -2,
        max: 2
      },
      grid: {
        backgroundColor: "#fffaff"
      },
      // Default DD Mode set to 'zoom'
      selection: {
        action: 'zoom'
      },
      tooltip: false,   // disable tooltip
      // Base series which is applied to all series
      baseSeries: {
        selectable: false
      }
    }]
  });
  var flot = win.findById('flot');

  // Replace Property Window
  flot.propertyCmp = new Ext.Window({
    title: 'Replaced Property Window',
    closeAction: 'hide',
    html: '<h1 style="padding: 24px">Property is currently disabled!</h1>'
  });

  // Replace contextMenu
  flot.contextMenu = [{
    text: 'Replaced Context Menu'
  },'-',{
    text: 'Property',
    handler: function() {
      this.showProperty();
    },
    scope: flot
  }];

  win.show();
});
