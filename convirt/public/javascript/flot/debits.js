/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, December 2008
 */

Ext.onReady(function() {

  var store = new Ext.data.Store({
    url: 'debits.xml',
    reader: new Ext.data.XmlReader({
      root: 'Debits',
      record: 'Debit',
      id: 'id',
      fields: ['id', 'enCours','archive','dateDebit','depose']
    }),
  });

  // Line Chart by id
  var flot_id_win = new Ext.Window({
    title: 'Line Chart by id (debits.xml)',
    x: 0,
    y: 0,
    width: 300,
    height: 300,
    layout: 'fit',
    items: [{
      xtype: 'flot',
      cls: 'x-panel-body',
      series: []
    }]
  });
  flot_id_win.show();
  var flot_id = flot_id_win.findByType('flot')[0];
  store.on('load', function(store, records, options) {
    var series = this.createSeries(store, 'id');
    this.plot(series);
    this.baseRanges = this.getRanges();
  }, flot_id);

  // Line Chart by dateDebit
  var flot_date_win = new Ext.Window({
    title: 'Line Chart by dateDebit (debits.xml)',
    x: 300,
    y: 0,
    width: 300,
    height: 300,
    layout: 'fit',
    items: [{
      xtype: 'flot',
      cls: 'x-panel-body',
      xaxis: { mode: 'time' },
      yaxis: { min:0, max: 100 },
      series: []
    }]
  });
  flot_date_win.show();
  var flot_date = flot_date_win.findByType('flot')[0];
  store.on('load', function(store, records, options) {
    var series = this.createSeries(store, 'dateDebit');
    for (var i = 0; i < series.length; i++) {
      var data = series[i].data;
      for (var j = 0; j < data.length; j++) {
        data[j][0] = Date.parseDate(data[j][0], "Y-m-d H:i:s.u");
      }
    }
    this.plot(series);
    this.baseRanges = this.getRanges();
  }, flot_date);

  // Bar Chart by id
  var barflot_win = new Ext.Window({
    title: 'Bar Chart by id (debits.xml)',
    x: 0,
    y: 300,
    width: 300,
    height: 300,
    layout: 'fit',
    items: [{
      xtype: 'barflot',
      cls: 'x-panel-body',
      xaxis: { min: 0, max: 100 },
      yaxis: { min: 0, max: 100 },
      series: [
        { name: 'enCours',  label: 'enCours'  },
        { name: 'archive',  label: 'archive'  },
        { name: 'depose',   label: 'depose'   },
        { name: 'coffreld', label: 'coffreld' }
      ]
    }]
  });
  barflot_win.show();
  var barflot = barflot_win.findByType('flot')[0];
  store.on('load', function(store, records, options) {
    var data = [];
    for (var i = 0; i < records.length; i++) {
      data.push(Ext.apply({
        label: records[i].data.id, // set id as xField
      }, records[i].data));
    }
    this.updateData(data);
    this.baseRanges = this.getRanges();
  }, barflot);

  // Pie Chart of enCours by id 
  var pieflot_win = new Ext.Window({
    title: 'Pie Chart of enCours by id (debits.xml)',
    x: 300,
    y: 300,
    width: 300,
    height: 300,
    layout: 'fit',
    items: [{
      xtype: 'pieflot',
      cls: 'x-panel-body',
      pies: {show: true, fillOpacity: 1 },
      series: []
    }]
  });
  pieflot_win.show();
  var pieflot = pieflot_win.findByType('flot')[0];
  store.on('load', function(store, records, options) {
    var series = this.createSeries(store, 'id', 'enCours');
    this.plot(series);
    this.baseRanges = this.getRanges();
  }, pieflot);

  store.load({});

});
