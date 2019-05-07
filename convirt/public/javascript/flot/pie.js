/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, December 2008
 */

Ext.QuickTips.init();

Ext.onReady(function() {
//  var win1 = new Ext.Window({
//    title: '2008 Web Browser Market Share',
//    id: 'browser_pie',
//    x: 0,
//    y: 0,
//    width: 400,
//    height: 400,
//    layout: 'fit',
//    items: [{
//      xtype: 'pieflot',
//      cls: 'x-panel-body',
//      legend: {show: false},
//      pies: {show: true, fillOpacity: 1 },
//      series: [
//        { label: 'IE 6',           data: [[0, 20.46]]},
//        { label: 'IE 7',           data: [[0, 46.77]]},
//        { label: 'IE 8',           data: [[0,  0.82]]},
//        { label: 'FF 2',           data: [[0,  3.77]]},
//        { label: 'FF 3',           data: [[0, 17.18]]},
//        { label: 'Safari',         data: [[0,  7.93]]},
//        { label: 'Chrome',         data: [[0,  1.04]]},
//        { label: 'Opera',          data: [[0,  0.71]]},
//        { label: 'Other Browsers', data: [[0,  0.0 ]]}
//      ]
//    }]
//  });
//  win1.show();

  var win2 = new Ext.Window({
    title: '2008 U.S. Car Market Share',
    id: 'car_pie',
//    x: 400,
//    y: 0,
    width: 800,
    height: 600,
    layout: 'fit',
    items: [{
      xtype: 'pieflot',
      cls: 'x-panel-body',
      pies: {show: true, autoScale: true,
          fillOpacity: 1 },
      series: [
        { label: 'General Motors', data: [[0, 100]]},
        { label: 'Ford Motor',     data: [[0, 19]]},
        { label: 'Chrysler',       data: [[0, 153]]},
        { label: 'TOYOTA',         data: [[0, 221]]},
        { label: 'Honda',          data: [[0, 142]]}
//        { label: 'Nissan',         data: [[0,  951350]]},
//        { label: 'Mazda',          data: [[0,  263949]]},
//        { label: 'MITSUBISHI',     data: [[0,   97257]]},
//        { label: 'ISUZU',          data: [[0,    4758]]},
//        { label: 'SUBARU',         data: [[0,  187699]]},
//        { label: 'SUZUKI',         data: [[0,   84865]]},
//        { label: 'Hyundai',        data: [[0,  401742]]},
//        { label: 'Kia',            data: [[0,  273397]]},
//        { label: 'BMW',            data: [[0,  303190]]},
//        { label: 'VOLVO',          data: [[0,   73102]]},
//        { label: 'Mercedes-Benz',  data: [[0,  225128]]},
//        { label: 'Saab',           data: [[0,   21368]]},
//        { label: 'Audi',           data: [[0,   87760]]},
//        { label: 'Porsche',        data: [[0,   26035]]}
      ]
    }]
  });
  win2.show();

//  var win3 = new Ext.Window({
//    title: [
//      '2008 Web Browser Market Share',
//      '(Pie chart support of r148 does not work well in bar chart)'
//    ].join('<br>'),
//    id: 'browser_bar',
//    x: 0,
//    y: 400,
//    width: 400,
//    height: 400,
//    layout: 'fit',
//    items: [{
//      xtype: 'flot',
//      cls: 'x-panel-body',
//      bars: {show: true, align: 'center', barWidth: 1},
//      xaxis: {
//        ticks: [
//          [0, 'IE 6'],
//          [1, 'IE 7'],
//          [2, 'IE 8'],
//          [3, 'FF 2'],
//          [4, 'FF 3'],
//          [5, 'Safari'],
//          [6, 'Chrome'],
//          [7, 'Opera'],
//          [8, 'Other Browsers']
//        ]
//      },
//      yaxis: { max: 100 },
//      series: [
//        { data: [[0, 20.46]]},
//        { data: [[1, 46.77]]},
//        { data: [[2,  0.82]]},
//        { data: [[3,  3.77]]},
//        { data: [[4, 17.18]]},
//        { data: [[5,  7.93]]},
//        { data: [[6,  1.04]]},
//        { data: [[7,  0.71]]},
//        { data: [[8,  0.0 ]]}
//      ]
//    }]
//  });
//  win3.show();

  var win4 = new Ext.Window({
    title: [
      '2008 U.S. Car Market Share',
      '(Pie chart support of r148 does not work well in bar chart)'
    ].join('<br>'),
    id: 'car_bar',
    x: 400,
    y: 400,
    width: 400,
    height: 400,
    layout: 'fit',
    items: [{
      xtype: 'flot',
      cls: 'x-panel-body',
      bars: {show: true, align: 'center', barWidth: 1},
      xaxis: {
        ticks: [
          [ 0, 'General Motors'],
          [ 1, 'Ford Motor'],
          [ 2, 'Chrysler'],
          [ 3, 'TOYOTA'],
          [ 4, 'Honda'],
          [ 5, 'Nissan'],
          [ 6, 'Mazda'],
          [ 7, 'MITSUBISHI'],
          [ 8, 'ISUZU'],
          [ 9, 'SUBARU'],
          [10, 'SUZUKI'],
          [11, 'Hyundai'],
          [12, 'Kia'],
          [13, 'BMW'],
          [14, 'VOLVO'],
          [15, 'Mercedes-Benz'],
          [16, 'Saab'],
          [17, 'Audi'],
          [18, 'Porsche']
        ]
      },
      series: [
        { label: 'General Motors', data: [[ 0, 2933451]]},
        { label: 'Ford Motor',     data: [[ 1, 1908806]]},
        { label: 'Chrysler',       data: [[ 2, 1453122]]},
        { label: 'TOYOTA',         data: [[ 3, 2217662]]},
        { label: 'Honda',          data: [[ 4, 1428765]]},
        { label: 'Nissan',         data: [[ 5,  951350]]},
        { label: 'Mazda',          data: [[ 6,  263949]]},
        { label: 'MITSUBISHI',     data: [[ 7,   97257]]},
        { label: 'ISUZU',          data: [[ 8,    4758]]},
        { label: 'SUBARU',         data: [[ 9,  187699]]},
        { label: 'SUZUKI',         data: [[10,   84865]]},
        { label: 'Hyundai',        data: [[11,  401742]]},
        { label: 'Kia',            data: [[12,  273397]]},
        { label: 'BMW',            data: [[13,  303190]]},
        { label: 'VOLVO',          data: [[14,   73102]]},
        { label: 'Mercedes-Benz',  data: [[15,  225128]]},
        { label: 'Saab',           data: [[16,   21368]]},
        { label: 'Audi',           data: [[17,   87760]]},
        { label: 'Porsche',        data: [[18,   26035]]}
      ]
    }]
  });
  win4.show();
});
