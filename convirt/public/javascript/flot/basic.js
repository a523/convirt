/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license or Ext Open Source License by NCS, December 2008
 */

function ppp() {

    var d1 = [[1, 3],[2,5], [3, 8], [4,6], [5, 4] ,[6, 2] ,[7, 1]]

    var month = ["jan", "feb", "mar"]
   
    var d2 = [[1, 3],[2,2], [3, 3], [4,4], [5, 2] ,[6, 2.5] ,[7, 2]]

    var d3 = [];
    for (var i = 0; i < 14; i += 0.5)
        d3.push([i, Math.cos(i)]);

    var d4 = [];
    for (var i = 0; i < 14; i += 0.1)
        d4.push([i, Math.sqrt(i * 10)]);

    var d5 = [];
    for (var i = 0; i < 14; i += 0.5)
        d5.push([i, Math.sqrt(i)]);
    

    $.plot($("#placeholder"), [
        {
            color:0,
            label: 'CPU Usage',
            //xaxis:{mode:"time",min: null,max:null,labelWidth:null,labelHeight:null,ticks:3},
            data: d1,
            lines: { show: true, fill: false}
        }
       ]);

     $.plot($("#placeholders"),  [
        { label: 'UP',           data: [[0,   236]]},
        { label: 'DOWN',           data: [[0,   87]]},
        { label: 'MAINT',        data: [[0,   126]]}
       ],
        {
            color:1,
            xaxis: {
              autoscaleMargin:1
            },
            pies: {show: true, fillOpacity: 1,fill: true }

        }
    );

//    $.plot($("#placeholdert"), [
//        {
//            color:0,
//            label:"Hard Disk Usage",
//            data: d2,
//            xaxis:1,
//            bars: { show: true, fill: true }
//        }
//    ]);
};
