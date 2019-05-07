/* $Id:$
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 * Released under the MIT license and Ext Open Source License by Kiyoto SUZUKI, 2008-2009
 *
 * Project Home: http://code.google.com/p/extflot/
 * API Documentation: http://code.google.com/p/extflot/wiki/ApiDocumentation
 * Live Demo: http://extflot.googlecode.com/svn/trunk/index.html
 */

// dummy for no GetText
if (typeof _  != "function") {  _ = function(str) { return str; }; }

/**
 * @class Ext.ux.Flot
 * @extends Ext.BoxComponent
 * <a href='http://code.google.com/p/extflot/'>http://code.google.com/p/extflot/</a>
 * <br>
 * flot is chart plotting library based on jQuery
 *   <a href='http://code.google.com/p/flot/'>http://code.google.com/p/flot/</a>
 * <br>
 * Ext Flot depends on the followings.
<pre>
 Ext JS   2.2 and 2.2.1
 flot     0.5 (or latest revision of flot (r153 or later))
 Ext Flot 0.10
</pre>
 * <br>
 * About original flot API, please see <a href='http://flot.googlecode.com/svn/trunk/API.txt'>http://flot.googlecode.com/svn/trunk/API.txt</a>.
 *
 *<hr>
 *
 * Flot Reference
 *<br><br>
 * Consider a call to the plot function:
<pre>
   var plot = $.plot(placeholder, data, options)
</pre>
 *
 * The placeholder is a jQuery object or DOM element or jQuery expression that the plot will be put into. 
 * This placeholder needs to have its width and height set as explained in the README (go read that now if you haven't, it's short). 
 * The plot will modify some properties of the placeholder so it's recommended you simply pass in a div that you don't use for anything else. 
 * Make sure you check any fancy styling you apply to the div, e.g. background images have been reported to be a problem on IE 7.
 *<br><br>
 * The format of the data is documented below, as is the available options. 
 * The "plot" object returned has some methods you can call.
 * These are documented separately below.
 *<br><br>
 * Note that in general Flot gives no guarantees if you change any of the objects you pass in to the plot function or get out of it 
 * since they're not necessarily deep-copied.
 *<br><br>
 * The data is an array of data series:
<pre>
  [ series1, series2, ... ]
</pre>
 *
 * A series can either be raw data or an object with properties. 
 * The raw data format is an array of points:
<pre>
  [ [x1, y1], [x2, y2], ... ]
</pre>
 * E.g.
<pre>
  [ [1, 3], [2, 14.01], [3.5, 3.14] ]
</pre>
 * 
 * Note that to simplify the internal logic in Flot both the x and y values must be numbers, 
 * even if specifying time series (see below for how to do this). 
 * This is a common problem because you might retrieve data from the database and serialize them directly to JSON without noticing the wrong type. 
 * If you're getting mysterious errors, double check that you're inputting numbers and not strings.
 *<br><br>
 * If a null is specified as a point or if one of the coordinates is null or couldn't be converted to a number, the point is ignored when drawing. 
 * As a special case, a null value for lines is interpreted as a line segment end, i.e. 
 * the point before and after the null value are not connected.
 *<br><br>
 * Lines and points take two coordinates. For bars, you can specify a third coordinate which is the bottom of the bar (defaults to 0).
 *<br><br>
 * The format of a single series object is as follows:
<pre>
  {
    color: color or number
    data: rawdata
    label: string
    lines: specific lines options
    bars: specific bars options
    points: specific points options
    threshold: specific threshold options
    xaxis: 1 or 2
    yaxis: 1 or 2
    clickable: boolean
    hoverable: boolean
    shadowSize: number
  }
</pre>
 * You don't have to specify any of them except the data, the rest are options that will get default values. 
 * Typically you'd only specify label and data, like this:
<pre>
  {
    label: "y = 3",
    data: [[0, 3], [10, 3]]
  }
</pre>
 * 
 * The label is used for the legend, if you don't specify one, 
 * the series will not show up in the legend.
 *<br><br>
 * If you don't specify color, the series will get a color from the auto-generated colors. 
 * The color is either a CSS color specification (like "rgb(255, 100, 123)") or 
 * an integer that specifies which of auto-generated colors to select, 
 * e.g. 0 will get color no. 0, etc.
 *<br><br>
 * The latter is mostly useful if you let the user add and remove series,
 * in which case you can hard-code the color index to prevent the colors
 * from jumping around between the series.
 *<br><br>
 * The "xaxis" and "yaxis" options specify which axis to use, specify 2
 * to get the secondary axis (x axis at top or y axis to the right).
 * E.g., you can use this to make a dual axis plot by specifying { yaxis: 2 } for one data series.
 *<br><br>
 * "clickable" and "hoverable" can be set to false to disable interactivity for specific series 
 * if interactivity is turned on in plot, see below.
 *<br><br>
 * The rest of the options are all documented below as they are the same
 * as the default options passed in via the options parameter in the plot
 * commmand. When you specify them for a specific data series, 
 * they will override the default options for the plot for that data series.
 *<br><br>
 * Here's a complete example of a simple data specification:
 * 
<pre>
  [ { label: "Foo", data: [ [10, 1], [17, -14], [30, 5] ] },
    { label: "Bar", data: [ [11, 13], [19, 11], [30, -7] ] } ]
</pre>
 *
 * @constructor
 * @param {Object} config configuration object
 */
Ext.ux.Flot = Ext.extend(Ext.BoxComponent, {
  // protected version of Ext Flot
  version: "0.10",

  /**
   * @cfg {Object} series 
   * flot series option
   */
  /**
   * @cfg {Object} baseSeries
   * The base options of each series.
   * It is applied by Ext.apply(), not Ext.applyIf().
   */
  /**
   * @cfg {String} type 
   * Base type of each column
   * It is used on {@link Ext.data.Record.create}
   *   'auto', 'string' 'int',  'float', 'boolean',  'date'
   */
  type: 'auto',
  /**
   * @cfg {Function} sortType 
   * The sort type of each column.
   * It is one of {@link Ext.data.SortTypes} 
   * Default is {@link Ext.data.SortTypes.asFloat}
   * It is used on {@link Ext.data.Record.create}
   */
  sortType: Ext.data.SortTypes.asFloat,

  /**
   * @cfg {Object} legend
   * Flot legend options. It is passed to flot with not modified.
   *
<pre>
  legend: {
    show: boolean
    labelFormatter: null or (fn: string, series object -> string)
    labelBoxBorderColor: color
    noColumns: number
    position: "ne" or "nw" or "se" or "sw"
    margin: number of pixels or [x margin, y margin]
    backgroundColor: null or color
    backgroundOpacity: number between 0 and 1
    container: null or jQuery object/DOM element/jQuery expression
  }
</pre>
   * 
   * The legend is generated as a table with the data series labels and small label boxes with the color of the series. 
   * If you want to format the labels in some way, 
   * e.g. make them to links, you can pass in a function for "labelFormatter". 
   * Here's an example that makes them clickable:
<pre>
  labelFormatter: function(label, series) {
    // series is the series object for the label
    return '<a href="#' + label + '">' + label + '</a>';
  }
</pre>
   * 
   * "noColumns" is the number of columns to divide the legend table into.
   * "position" specifies the overall placement of the legend within the plot (top-right, top-left, etc.) 
   * and margin the distance to the plot edge (this can be either a number or an array of two numbers like [x, y]). 
   * "backgroundColor" and "backgroundOpacity" specifies the background. 
   * The default is a partly transparent auto-detected background.
   *<br><br>
   * If you want the legend to appear somewhere else in the DOM, 
   * you can specify "container" as a jQuery object/expression to put the legend table into. 
   * The "position" and "margin" etc. options will then be ignored. 
   * Note that Flot will overwrite the contents of the container.
   * Most of the above settings do not apply
   */

  /**
   * @cfg {Object} xaxis
   * flot xaxis
   *
<pre>
  xaxis, yaxis, x2axis, y2axis: {
    mode: null or "time"
    min: null or number
    max: null or number
    autoscaleMargin: null or number
    labelWidth: null or number
    labelHeight: null or number

    ticks: null or number or ticks array or (fn: range -> ticks array)
    tickSize: number or array
    minTickSize: number or array
    tickFormatter: (fn: number, object -> string) or string
    tickDecimals: null or number
  }
</pre>
   * 
   * All axes have the same kind of options. The "mode" option determines how the data is interpreted, 
   * the default of null means as decimal numbers. 
   * Use "time" for time series data, see the next section.
   *<br><br>
   * The options "min"/"max" are the precise minimum/maximum value on the scale. 
   * If you don't specify either of them, a value will automatically
   * be chosen based on the minimum/maximum data values.
   *<br><br>
   * The "autoscaleMargin" is a bit esoteric: it's the fraction of margin
   * that the scaling algorithm will add to avoid that the outermost points
   * ends up on the grid border. 
   * Note that this margin is only applied when a min or max value is not explicitly set. 
   * If a margin is specified, the plot will furthermore extend the axis end-point to the nearest whole tick. 
   * The default value is "null" for the x axis and
   * 0.02 for the y axis which seems appropriate for most cases.
   *<br><br>
   * "labelWidth" and "labelHeight" specifies the maximum size of the tick labels in pixels. 
   * They're useful in case you need to align several plots.
   *<br><br>
   * The rest of the options deal with the ticks.
   *<br><br>
   * If you don't specify any ticks, a tick generator algorithm will make some for you. 
   * The algorithm has two passes. 
   * It first estimates how many ticks would be reasonable and uses this number to compute a nice round tick interval size. 
   * Then it generates the ticks.
   *<br><br>
   * You can specify how many ticks the algorithm aims for by setting "ticks" to a number. 
   * The algorithm always tries to generate reasonably round tick values so even if you ask for three ticks, 
   * you might get five if that fits better with the rounding. 
   * If you don't want any ticks at all, set "ticks" to 0 or an empty array.
   *<br><br>
   * Another option is to skip the rounding part and directly set the tick interval size with "tickSize". 
   * If you set it to 2, you'll get ticks at 2, 4, 6, etc. 
   * Alternatively, you can specify that you just don't want
   * ticks at a size less than a specific tick size with "minTickSize".
   * Note that for time series, the format is an array like [2, "month"], see the next section.
   *<br><br>
   * If you want to completely override the tick algorithm, you can specify an array for "ticks", either like this:
<pre>
   ticks: [0, 1.2, 2.4]
</pre>
   * 
   * Or like this where the labels are also customized:
<pre>
   ticks: [[0, "zero"], [1.2, "one mark"], [2.4, "two marks"]]
</pre>
   * 
   * You can mix the two if you like.
   *<br><br>
   * For extra flexibility you can specify a function as the "ticks" parameter. 
   * The function will be called with an object with the axis min and max and should return a ticks array. 
   * Here's a simplistic tick generator that spits out intervals of pi, 
   * suitable for use on the x axis for trigonometric functions:
<pre>
  function piTickGenerator(axis) {
    var res = [], i = Math.floor(axis.min / Math.PI);
    do {
      var v = i * Math.PI;
      res.push([v, i + "\u03c0"]);
      ++i;
    } while (v < axis.max);
    
    return res;
  }
</pre>
   * 
   * You can control how the ticks look like with "tickDecimals", the number of decimals to display (default is auto-detected).
   *<br><br>
   * Alternatively, for ultimate control over how ticks look like you can provide a function to "tickFormatter". 
   * The function is passed two parameters, the tick value and an "axis" object with information, 
   * and should return a string. The default formatter looks like this:
<pre>
  function formatter(val, axis) {
    return val.toFixed(axis.tickDecimals);
  }
</pre>
   *
   * The axis object has "min" and "max" with the range of the axis,
   * "tickDecimals" with the number of decimals to round the value to and
   * "tickSize" with the size of the interval between ticks as calculated
   * by the automatic axis scaling algorithm (or specified by you). 
   * Here's an example of a custom formatter:
<pre>
  function suffixFormatter(val, axis) {
    if (val > 1000000)
      return (val / 1000000).toFixed(axis.tickDecimals) + " MB";
    else if (val > 1000)
      return (val / 1000).toFixed(axis.tickDecimals) + " kB";
    else
      return val.toFixed(axis.tickDecimals) + " B";
  }
</pre>
   *
   *<hr>
   *
   * Time series data
   *<br><br>
   * Time series are a bit more difficult than scalar data because calendars don't follow a simple base 10 system. 
   * For many cases, Flot abstracts most of this away, but it can still be a bit difficult to
   * get the data into Flot. So we'll first discuss the data format.
   *<br><br>
   * The time series support in Flot is based on Javascript timestamps,
   * i.e. everywhere a time value is expected or handed over, a Javascript timestamp number is used. 
   * This is a number, not a Date object. 
   * A Javascript timestamp is the number of milliseconds since January 1,
   * 1970 00:00:00 UTC. This is almost the same as Unix timestamps, except it's in milliseconds, so remember to multiply by 1000!
   *<br><br>
   * You can see a timestamp like this
<pre>
  alert((new Date()).getTime())
</pre>
   * 
   * Normally you want the timestamps to be displayed according to a certain time zone, 
   * usually the time zone in which the data has been produced. 
   * However, Flot always displays timestamps according to UTC.
   * It has to as the only alternative with core Javascript is to interpret
   * the timestamps according to the time zone that the visitor is in,
   * which means that the ticks will shift unpredictably with the time zone
   * and daylight savings of each visitor.
   *<br><br>
   * So given that there's no good support for custom time zones in Javascript, 
   * you'll have to take care of this server-side.
   *<br><br>
   * The easiest way to think about it is to pretend that the data production time zone is UTC, even if it isn't. 
   * So if you have a datapoint at 2002-02-20 08:00, you can generate a timestamp for eight o'clock UTC even if it really happened eight o'clock UTC+0200.
   *<br><br>
   * In PHP you can get an appropriate timestamp with 'strtotime("2002-02-20 UTC") * 1000', 
   * in Python with 'calendar.timegm(datetime_object.timetuple()) * 1000', 
   * in .NET with something like:
   *
<pre>
  public static int GetJavascriptTimestamp(System.DateTime input)
  {
    System.TimeSpan span = new System.TimeSpan(System.DateTime.Parse("1/1/1970").Ticks);
    System.DateTime time = input.Subtract(span);
    return (long)(time.Ticks / 10000);
  }
</pre>
   * 
   * Javascript also has some support for parsing date strings, 
   * so it is possible to generate the timestamps manually client-side.
   *<br><br>
   * If you've already got the real UTC timestamp, it's too late to use the pretend trick described above. 
   * But you can fix up the timestamps by adding the time zone offset, e.g. 
   * for UTC+0200 you would add 2 hours to the UTC timestamp you got. 
   * Then it'll look right on the plot. 
   * Most programming environments have some means of getting the timezone
   * offset for a specific date (note that you need to get the offset for
   * each individual timestamp to account for daylight savings).
   *<br><br>
   * Once you've gotten the timestamps into the data and specified "time" as the axis mode, 
   * Flot will automatically generate relevant ticks and format them. 
   * As always, you can tweak the ticks via the "ticks" option
   *<br><br>
   * just remember that the values should be timestamps (numbers), not Date objects.
   *<br><br>
   * Tick generation and formatting can also be controlled separately through the following axis options:
   *
<pre>
  minTickSize: array
  timeformat: null or format string
  monthNames: null or array of size 12 of strings
</pre>
   *
   * Here "timeformat" is a format string to use. You might use it like this:
<pre>
  xaxis: {
    mode: "time"
    timeformat: "%y/%m/%d"
  }
</pre>
   *
   * This will result in tick labels like "2000/12/24". 
   * The following specifiers are supported
<pre>
  %h': hours
  %H': hours (left-padded with a zero)
  %M': minutes (left-padded with a zero)
  %S': seconds (left-padded with a zero)
  %d': day of month (1-31)
  %m': month (1-12)
  %y': year (four digits)
  %b': month name (customizable)
</pre>
   *
   * You can customize the month names with the "monthNames" option. 
   * For instance, for Danish you might specify:
<pre>
  monthNames: ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
</pre>
   * 
   * The format string and month names are used by a very simple built-in format function that takes a date object, 
   * a format string (and optionally an array of month names) and returns the formatted string. 
   * If needed, you can access it as $.plot.formatDate(date, formatstring, monthNames) 
   * or even replace it with another more advanced function from a date library if you're feeling adventurous.
   *<br><br>
   * If everything else fails, you can control the formatting by specifying a custom tick formatter function as usual. 
   * Here's a simple example which will format December 24 as 24/12:
   *
<pre>
  tickFormatter: function (val, axis) {
    var d = new Date(val);
    return d.getUTCDate() + "/" + (d.getUTCMonth() + 1);
  }
</pre>
   * 
   * Note that for the time mode "tickSize" and "minTickSize" are a bit
   * special in that they are arrays on the form "[value, unit]" where unit
   * is one of "second", "minute", "hour", "day", "month" and "year". 
   * So you can specify
<pre>
  minTickSize: [1, "month"]
</pre>
   * 
   * to get a tick interval size of at least 1 month and correspondingly,
   * if axis.tickSize is [2, "day"] in the tick formatter, the ticks have been produced with two days in-between.
   */
  /**
   * @cfg {Object} yaxis
   * flot yaxis
   * see also xaxis
   */
  /** 
   * @cfg {Object} x2axis
   * flot x2axis
   * see also xaxis
   */
  /**
   * @cfg {Object} y2axis
   * flot y2axis
   * see also xaxis
   */

  /**
   * @cfg {Object} lines
   * flot lines
   *<br><br>
   * The most important options are "lines", "points", "bars" and "pies"
   * that specifies whether and how lines, points and bars should be shown for each data series. 
   * In case you don't specify anything at all, Flot will default to showing lines 
   * (you can turn this off with lines: { show: false}). 
   * You can specify the various types independently of each other, 
   * and Flot will happily draw each of them in turn, e.g.
   *
<pre>
  var options = {
    lines: { show: true, fill: true, fillColor: "rgba(255, 255, 255, 0.8)" },
    points: { show: true, fill: false }
  };
</pre>
   *
   * "lineWidth" is the thickness of the line or outline in pixels. 
   * You can set it to 0 to prevent a line or outline from being drawn; 
   * this will also hide the shadow.
   *<br><br>
   * "fill" is whether the shape should be filled. For lines, this produces area graphs. 
   * You can use "fillColor" to specify the color of the fill.
   * If "fillColor" evaluates to false (default for everything except points which are filled with white), 
   * the fill color is auto-set to the color of the data series. 
   * You can adjust the opacity of the fill by setting fill to a number between 0 
   * (fully transparent) and 1 (fully opaque).
   *<br><br>
   * For lines, "steps" specifies whether two adjacent data points are connected with 
   * a straight (possibly diagonal) line or with first a horizontal and then a vertical line.
   */
  /**
   * @cfg {Object} points
   * flot points
   * see also lines
   */
  /**
   * @cfg {Object} bars
   * flot bars
   * see also lines
   *<br><br>
<pre>
  bars: {
    barWidth: number
    align: "left" or "center"
    horizontal: boolean
  }
</pre>
   * For bars, fillColor can be a gradient, see the gradient documentation below. 
   * "barWidth" is the width of the bars in units of the x axis,
   * contrary to most other measures that are specified in pixels. 
   * For instance, for time series the unit is milliseconds so 24 * 60 * 60 * 1000 produces bars with the width of a day. 
   * "align" specifies whether a bar should be left-aligned (default) or centered on top of the value it represents. 
   * When "horizontal" is on, the bars are drawn horizontally, i.e. from the y axis instead of the x axis; 
   * note that the bar end points are still defined in the same way so you'll
   * probably want to swap the coordinates if you've been plotting vertical bars first.
   */
  /**
   * @cfg {Object} pies
   * Flot pies
   * see also lines
   *<br><br>
<pre>
  pies: {
    show: false,
    radius: null,         // or number by px
    labelRadius: null,    // or number by px
    startAngle: 0,
    fill: true,
    fillColor: null,
    // null or fn or 'value', 'percent', 'label', 'full'
    // fn: (label, value, percent, textValue, pie, serie, options) -> html
    labelFormatter: null, 
    labelStyle: 'font-size: normal; font-weight: bold; color:#545454;',
    bias: [0.3, -1.4, 0.1], // [init, step, threshold]
  }
</pre>
   * "radius" is the radius of pie. 
   * If you specify it by number, it passed as the pie radius.
   * If you specify it by null or nothing, the flot determines it by plot area.
   * If legend is shown, radius become smaller.
   *<br><br>
   * "labelRadius" is the radius or label area.
   * If you specify it by number, it passed as the label radius.
   * If you specify it by null or nothing, the flot determines it by pie radius.
   *<br><br>
   * "labelFormatter" is the formatter of each series label.
   * If you specify it by function, like the followings:
<pre>
labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
  return textValue + '%<br><span style="font-size: 75%">' + label + '<br>(' + value + ')</span>';
  
}
</pre>
   * <li>label: the label of the serie</li>
   * <li>value: the raw value of the serie</li>
   * <li>percent: the raw percent value</li>
   * <li>textValue: the percent to show. you should add '%' after it.</li>
   * <li>pie: the pie informations to show. it contains the following members.
<pre>
radius labelRadius sumSeries anchorX anchorY labelX labelY startAngle endAngle sliceMiddle
</pre>
   * </li>
   * <li>serie: the serie to show in this pie</li>
   * <li>options: flot options which is parsed</li>
   *<br><br>
   * "labelStyle" is the style of label div. You can specify it in .pieLabel class
   *<br><br>
   * "bias" is the option to ajust position of small pie.
   * You specify it as Array.
   * <li>0: initial value of bias</li>
   * <li>1: the bias for the next bias</li>
   * <li>2: threshold to apply bias. if the percent is smaller than it, the pecent will be biased.</li>
   * If you specify null, bias is disabled.
   */

  /**
   * @cfg {Array} colors
   * Flot colors
   *<br><br>
   * The "colors" array specifies a default color theme to get colors for the data series from. 
   * You can specify as many colors as you like, like this:
   *
<pre>
  colors: ["#d18b2c", "#dba255", "#919733"]
</pre>
   *
   * If there are more data series than colors, Flot will try to generate extra colors by lightening and darkening colors in the theme.
   *<br><br>
   * A gradient is specified like this:
   *
<pre> 
  { colors: [ color1, color2, ... ] }
</pre>
   * 
   * For instance, you might specify a background on the grid going from black to gray like this:
   *
<pre>
  grid: {
    backgroundColor: { colors: ["#000", "#999"] }
  }
</pre>
   * 
   * For the series you can specify the gradient as an object 
   * that specifies the scaling of the brightness and the opacity of the series color, e.g.
   *
<pre>
  { colors: [{ opacity: 0.8 }, { brightness: 0.6, opacity: 0.8 } ]
</pre>
   * 
   * where the first color simply has its alpha scaled, whereas the second is also darkened.
   *<br><br>
   * Flot currently only supports vertical gradients drawn from top to bottom because that's what works with IE.
   */

  /**
   * @cfg {Number} shadowSize
   * flot shadowSize
   *
   *"shadowSize" is the default size of shadows in pixels. Set it to 0 to remove shadows.
   */
  /** 
   * @cfg {Object} threshold
   * flot threshold
   * This is not supported in flot 0.5
   *
<pre>
  threshold: {
    below: number
    color: color
  }
</pre>
   * 
   * "threshold" specifies that the data points below "below" should be
   * drawn with the specified color. This makes it easy to mark points
   * below 0, e.g. for budget data.
   */

  /**
   * @cfg {Object} grid
   * flot grid options
   *
<pre>
  grid: {
    color: color
    backgroundColor: color/gradient or null
    tickColor: color
    labelMargin: number
    markings: array of markings or (fn: axes -> array of markings)
    borderWidth: number
    borderColor: color or null
    clickable: boolean
    hoverable: boolean
    autoHighlight: boolean
    mouseActiveRadius: number
  }
</pre>
   * 
   * The grid is the thing with the axes and a number of ticks. "color" is
   * the color of the grid itself whereas "backgroundColor" specifies the
   * background color inside the grid area. 
   * The default value of null means that the background is transparent. 
   * You can also set a gradient, see the gradient documentation below.
   *<br><br>
   * "tickColor" is the color of the ticks and "labelMargin" is the spacing between tick labels and the grid. 
   * Note that you can style the tick labels with CSS, e.g. to change the color. 
   * They have class "tickLabel".
   * "borderWidth" is the width of the border around the plot. 
   * Set it to 0 to disable the border. 
   * You can also set "borderColor" if you want the border to have a different color than the grid lines.
   *<br><br>
   * "markings" is used to draw simple lines and rectangular areas in the background of the plot. 
   * You can either specify an array of ranges on the form 
<pre>
{ xaxis: { from, to }, yaxis: { from, to } } 
</pre>
   * (secondary axis coordinates with x2axis/y2axis) or with a function 
   * that returns such an array given the axes for the plot in an object as the first parameter.
   *<br><br>
   * You can set the color of markings by specifying "color" in the ranges object. 
   * Here's an example array:
<pre>
  markings: [ { xaxis: { from: 0, to: 2 }, yaxis: { from: 10, to: 10 }, color: "#bb0000" }, ... ]
</pre>
   * 
   * If you leave out one of the values, that value is assumed to go to the border of the plot. 
   * So for example if you only specify 
<pre>
{ xaxis: { from: 0, to: 2 } } 
</pre>
   * it means an area that extends from the top to the bottom of the plot in the x range 0-2.
   * 
   * A line is drawn if from and to are the same, e.g.
<pre>
  markings: [ { yaxis: { from: 1, to: 1 } }, ... ]
</pre>
   * 
   * would draw a line parallel to the x axis at y = 1. 
   * You can control the line width with "lineWidth" in the ranges objects.
   *<br><br>
   * An example function might look like this:
<pre>
  markings: function (axes) {
    var markings = [];
    for (var x = Math.floor(axes.xaxis.min); x < axes.xaxis.max; x += 2)
      markings.push({ xaxis: { from: x, to: x + 1 } });
    return markings;
  }
</pre>
   * 
   * If you set "clickable" to true, the plot will listen for click events on the plot area 
   * and fire a "plotclick" event on the placeholder with a position and a nearby data item object as parameters. 
   * The coordinates are available both in the unit of the axes (not in pixels) and in global screen coordinates.
   *<br><br>
   * Likewise, if you set "hoverable" to true, 
   * the plot will listen for mouse move events on the plot area and fire a "plothover" event 
   * with the ame parameters as the "plotclick" event. 
   * If "autoHighlight" is true (the default), nearby data items are highlighted automatically.
   * If needed, you can disable highlighting and control it yourself 
   * with the highlight/unhighlight plot methods described elsewhere.
   *<br><br>
   * You can use "plotclick" and "plothover" events like this:
<pre>
    $.plot($("#placeholder"), [ d ], { grid: { clickable: true } });

    $("#placeholder").bind("plotclick", function (event, pos, item) {
        alert("You clicked at " + pos.x + ", " + pos.y);
        // secondary axis coordinates if present are in pos.x2, pos.y2,
        // if you need global screen coordinates, they are pos.pageX, pos.pageY

        if (item) {
          highlight(item.series, item.datapoint);
          alert("You clicked a point!");
        }
    });
</pre>
   * 
   * The item object in this example is either null or a nearby object on the form:
<pre>
  item: {
      datapoint: the point as you specified it in the data, e.g. [0, 2]
      dataIndex: the index of the point in the data array
      series: the series object
      seriesIndex: the index of the series
      pageX, pageY: the global screen coordinates of the point
  }
</pre>
   * 
   * For instance, if you have specified the data like this 
   *
<pre>
    $.plot($("#placeholder"), [ { label: "Foo", data: [[0, 10], [7, 3]] } ], ...);
</pre>
   *
   * and the mouse is near the point (7, 3), "datapoint" is the [7, 3] we specified, 
   * "dataIndex" will be 1, "series" is a normalized series object with among other things 
   * the "Foo" label in series.label and the color in series.color, and "seriesIndex" is 0.
   *<br><br>
   * If you use the above events to update some other information and 
   * want to clear out that info in case the mouse goes away, 
   * you'll probably also need to listen to "mouseout" events on the placeholder div.
   *<br><br>
   * "mouseActiveRadius" specifies how far the mouse can be from an item and still activate it. 
   * If there are two or more points within this radius, 
   * Flot chooses the closest item. For bars, the top-most bar
   * (from the latest specified data series) is chosen.
   *<br><br>
   * If you want to disable interactivity for a specific data series, 
   * you can set "hoverable" and "clickable" to false in the options for that series, 
   * like this 
<pre>
{ data: [...], label: "Foo", clickable: false }.
</pre>
   * 
   * In Ext.ux.Flot, the 'clickable' and 'hoverable' are true by default.
   */
  /**
   * @cfg {Object} selection
   * flot selection option
   *
<pre>
  selection: {
    mode: null or "x" or "y" or "xy",
    color: color
  }
</pre>
   *
   * You enable selection support by setting the mode to one of "x", "y" or "xy". 
   * In "x" mode, the user will only be able to specify the x range, similarly for "y" mode. 
   * For "xy", the selection becomes a rectangle where both ranges can be specified. 
   * "color" is color of the selection.
   *<br><br>
   * When selection support is enabled, a "plotselected" event will be emitted
   * on the DOM element you passed into the plot function. The event
   * handler gets one extra parameter with the ranges selected on the axes,
   * like this:
<pre>
  placeholder.bind("plotselected", function(event, ranges) {
    alert("You selected " + ranges.xaxis.from + " to " + ranges.xaxis.to)
    // similar for yaxis, secondary axes are in x2axis
    // and y2axis if present
  });
</pre>
   * The "plotselected" event is only fired when the user has finished making the selection. 
   * A "plotselecting" event is fired during the process with the same parameters as the "plotselected" event, 
   * in case you want to know what's happening while it's happening,
   *<br><br>
   * A "plotunselected" event with no arguments is emitted when the user
   * clicks the mouse to remove the selection.
   *<br><br>
   * The followings are extension of Ext.ux.Flot
   *
<pre>
selection: {
  action:    'select' or 'zoom' or 'move' or null
  appendKey: 'shiftKey' or 'ctrlKey' or 'altKey'
  zoomDirection: 'tb' or 'bt' or 'lr' or 'rl'
  zoomWindow: 'ranges' or 'width' or 'height' or 'expand' or 'shrink'
  cursor: {
    select: 'default'
    zoom:   'crosshair'
    move:   'move'
  }
}
</pre>
   *
   * <li>Specify action on selected by 'action'
   *   <ol>
   *   <li>'select' is to select the data in the selected range.
   *     With shift key, append the data into current selected data.
   *     Normally, refresh the selected data.
   *     This is default value of 'action'.
   *   </li>
   *   <li>'zoom', is zooming in the selected range.
   *     upper = zoom-in lower = zoom-out
   *   </li>
   *   <li>'move' is to move the viewing area by same zoom-ratio</li>
   *   </ol>
   * </li>
   * <li>'appendKey' is the key configuration to append to selection.
   *   Specify it by DOM event name. (like 'shiftkey', etc...)
   * </li>
   * <li>'zoomDirection' is specification of direction of mouse moving for zoom-in and zoom-out.
<pre>
    zoom-in    zoom-out
tb: top        bottom
bt: bottom     top
lr: left       right
rl: right      left
</pre>
   * <li>'zoomWindow' is specification how to determine new display range.
   *   Default value is 'expand'.
   *   <ol>
   *   <li>'ranges' sets the new dispaly range as selected range. 
   *   In this case, the ratio of width and height changes between before zooming and after.
   *   <li>'width'  determines the new range from width of selected range.
   *   <li>'height' determines the new range from height of selected range.
   *   <li>'expand' determines the new range from the longer value of width and height.
   *   <li>'shrink' determines the new range from the shorter value of width and hegiht.
   *   </ol>
   *
   * </li>
   * <li>'cursor' specifies  the cursor of each mode
   * The following values are acceptable 
<pre>
crosshair, hand, move, text, wait, help, default, auto,
n-resize, s-resize, w-resize, e-resize, 
nw-resize, ne-resize, sw-resize, se-resize
</pre>
   * </li>
   * TODO Change the colors of selecting rectangle by each selection.action
   */
  /**
   * @cfg {Object} crosshair
   * flot crosshair option
   * This is not supported in flot 0.5
   *
<pre>
  crosshair: {
    mode: null or "x" or "y" or "xy"
    color: color
  }
</pre>
   * You can enable crosshairs, thin lines, that follow the mouse by setting the mode to one of "x", "y" or "xy". 
   * The "x" mode enables a vertical crosshair that lets you trace the values on the x axis, 
   * "y" enables a horizontal crosshair and "xy" enables them both.
   */

  /**
   * @cfg {Integer/String} width
   * Width of this Ext.ux.Flot instance
   * Not specifyed, the width is same as parent's.
   */
  /**
   * @cfg {Integer/String} height
   * Height of this Ext.ux.Flot instance
   * Not specifyed, the height is same as parent's.
   */
  /**
   * @property store
   * @type Ext.data.JsonStore
   * Mirrors of the series data
   */
  /**
   * @property clickItem
   * @type Object
   * Item of latest 'plotclick' event
   */
  /**
   * @property hoverItem
   * @type Object 
   * Item of latest 'plothover' event
   */
  /**
   * @property baseRanges
   * @type Object
   * The range for 100%
   * This is the format for 'plotselect'.
   */
  /**
   * @property currentRanges
   * @type Object
   * The range of current state (not 100%)
   * This is the format for 'plotselect'.
   */

  /**
   * @property contextMenu
   * @type Array
   * The menus to display at 'contextmenu' event.
   * This is a argument of <pre>new Ext.menu.Menu({ items: this.contextMenu })</pre>
   * If you want to add some items, 'push' or 'concat' them after creating
   * Ext.ux.Flot instance.
   */
  contextMenu: [{
    name: 'select',
    text: _('Select'),
    iconCls: 'cursor',
    handler: function() { this.setSelectionAction('select'); }
  },{
    name: 'zoom',
    text: _('Zoom'),
    iconCls: 'magnifier_zoom',
    handler: function() { this.setSelectionAction('zoom'); }
  },{
    name: 'move',
    text: _('Move'),
    iconCls: 'arrow_move',
    handler: function() { this.setSelectionAction('move'); }
  },'-',{
    name: 'actual',
    text: _('100%'),
    iconCls: 'magnifier_zoom_actual',
    handler: function() { 
      this.zoomRatio(1.0); 
    }
  },'-',{
    name: 'selectall',
    text: _('Select All'),
    //iconCls: 'shopping_basket__plus',
    handler: function() { this.selectAll(); }
  },{
    name: 'unselectall',
    text: _('Unselect All'),
    //iconCls: 'shopping_basket__exclamation',
    handler: function() { this.unselectAll(); }
  },'-',{
    name: 'property',
    text: _('Property'),
    iconCls: 'puzzle',
    handler: function() { this.showProperty(); }
  }],

  /**
   * @property datapointContextMenu
   * @type Array 
   * The menues to display at clicking some data points
   * Clicking some data points means the position of clicking is 
   * within 5 pixcels from this.clickItem.page{X|Y}.
   */
  datapointContextMenu: [{
    name: 'selectalldatapoint',
    text: _('Select All Points'),
    iconCls: 'flag_plus',
    handler: function() { 
      var item = this.clickItem || this.hoverItem;
      if (item) { this.selectAll(item.series); }
    }
  },{
    name: 'unselectalldatapoint',
    text: _('Unselect All Points'),
    iconCls: 'flag_minus',
    handler: function() { 
      var item = this.clickItem || this.hoverItem;
      if (item) { this.unselectAll(item.series); }
    }
  },'-',{
    name: 'showseries',
    text: _('Show Series'),
    iconCls: 'database_plus',
    handler: function() { 
      var item = this.clickItem || this.hoverItem;
      if (item) { this.setHidden(item.series, false); }
    }
  },{
    name: 'hideseries',
    text: _('Hide Series'),
    iconCls: 'database_minus',
    handler: function() { 
      var item = this.clickItem || this.hoverItem;
      if (item) { this.setHidden(item.series, true); }
    }
  }],

  /**
   * @cfg {Object} basePropertyColumn
   * Base configurations of columns of Ext Flot property grid. 
   * This is options {@link Ext.grid.ColumnModel}.
   */
  /**
   * @property propertyCmp
   * @type Ext.Component
   * This is Ext.Component instance of property grid. 
   * If you hook displaying it, listen 'show' event of propertyCmp 
   * You can replace and customize property grid.
   *
<pre>
var extflot = new Ext.ux.ExtFlot({
  ...
});
extflot.propertyCmp = new Ext.Window({
  title: 'My Proeprty'
});
</pre>
   *
   */

  /**
   * @cfg {Bool/String/Object} tooltip
   * This is standard Ext.Tooltip not QuickTips. 
   * <li>String: The value is format by XTemplate.
   * The following XTemplate arguments are avalable.
<pre>
{
   tipId:       event.target.id + '-tip',
   pageX:       pos.pageX,
   pageY:       pos.pageY,
   x:           pos.x,
   y:           pos.y,
   0:           dp[0],
   1:           dp[1],
   datapointX:  item.datapoint[0],
   datapointY:  item.datapoint[1],
   label:       item.series.label,
   color:       item.series.color,
   shadowSize:  item.series.shadowSize,
   dataIndex:   item.dataIndex,
   seriesIndex: item.seriesIndex,
   series:      item.series
}
</pre>
   * 0 and 1 are formatted item.datapoint value by tickFormatter.
   * <li>Boolean: If it is true, the following formatter is used.
<pre>
<div id="{tipId}">{label} ({0}, {1})</div>
</pre>
   * If it is false, disable tooltip.</li>
   * <li>Object: It is passed to the constructor of Ext.ToolTip</li>
   * <li>Function: formatter function. the return value is set to tooltip.html.</li>
   */
  tooltip: true,
  /**
   * @cfg {String} tooltipEvent
   * The event to show tooltip. Default is 'plothover'.
   *  <li>plothover 
   *  <li>plotclick
   *  <li>all (plothover and plotclick)
   */
  tooltipEvent: 'plothover',
  /**
   * @property disableTooltip
   * @type Bool
   * Current status to disable tooltip
   */

  /**
   * @property flot
   * @type Object
   * The flot instance which Ext Flot instance hold on. 
   * This is typically read-only. Please access by Ext Flot methods. 
   */

  // private
  initComponent: function() {
    // completion of configurations
    Ext.applyIf(this, {
      grid: {},
      xaxis: {},
      yaxis: {},
      selection: {},
      crosshair: {}
    });
    Ext.applyIf(this.grid, {
      clickable: true,
      hoverable: true
    });
    Ext.applyIf(this.selection, {
      mode:          "xy", 
      action:        'select',
      appendKey:     'shiftKey',
      zoomDirection: 'tb',
      zoomWindow:    'expand',
      cursor: {}
    });
    Ext.applyIf(this.selection.cursor, {
      select: 'default',
      zoom:   'crosshair',
      move:   'move'
    });

    // mirror the data 
    this.store = this.store || new Ext.data.JsonStore({});

    // data points of selected
    this.selected = [];

    // Craete Ext.Action for context menu
    this.actions = {};
    var keys = ['contextMenu', 'datapointContextMenu'];
    for (var k = 0; k < keys.length; k++) {
      var key = keys[k];
      if (this[key]) {
        var menu = [];
        var contextMenu = this[key];
        for (var i = 0, len = contextMenu.length; i < len; i++) {
          if (typeof contextMenu[i] == 'object') {
            var action = new Ext.Action(Ext.apply({scope: this}, contextMenu[i]));
            this.actions[contextMenu[i].name] = action;
            menu.push(action);
          } else {
            menu.push(contextMenu[i]);
          }
        }
        this[key] = menu;
      }
    }

    Ext.ux.Flot.superclass.initComponent.call(this);
    this.addEvents(
      /**
       * @event click
       * @param {OBject} event
       * Fire when clicked anywhere in Ext Flot instance area. 
       * This is Ext.Element (DOM) event. 
       * If you return false, Ext.ux.Flot do nothing.
       */
      "click",
      /**
       * @event dblclick
       * @param {OBject} event
       * Fire when dblclicked anywhere in Ext Flot instance area.
       * This is Ext.Element (DOM) event. 
       * If you return false, Ext.ux.Flot do nothing.
       */
      "dblclick",
      /**
       * @event contextmenu
       * @param {OBject} event
       * Fire before to show contextMenu.
       * If you return false, Ext.ux.Flot do nothing.
       */
      "contextmenu",
      /**
       * @event beforedraw
       * Fire before (re-)draw flot graph. 
       * If you return false, the drawing graph is not processed. 
       * @param {Ext.ux.Flot} this
       * @param {Object} series
       */
      "beforedraw",
      /**
       * @event draw
       * Fire after (re-)draw flot graph.
       * @param {Ext.ux.Flot} this
       * @param {Object} series
       */
      "draw",
      /**
       * @event plotselected
       * Fire when any datapoint is selected. 
       * This event enables when series.selectable is true. 
       * If you return false, Ext.ux.Flot do nothing.
       * 'Item' contains the following members. 
       * @param {Ext.ux.Flot} this
       * @param {Object} event event object
       * @param {Object} range the rectangle ranges selected 
       * {x: xpos, y: ypos, x2: xpos2, y2: ypos2}
       * @param {Object} item the items selected
       * If it is not null, the value contains selected data points, etc...
       * <li>datapoint Series and datapoint selected like [0, 2]
       * <li>dataIndex Index of datapoint in the serie
       * <li>series    The serie selected
       * <li>seriesIndex Index of serie in the series
       * <li>pageX     coordinate of selected point in browser window.
       * <li>pageY     coordinate of selected point in browser window.
       */
      "plotselected",
      /**
       * @event plotselecting
       * Fire when any datapoint is selecting (dragging). 
       * This event enables when series.selectable is true. 
       * If you return false, Ext.ux.Flot do nothing.
       * The arguments are same with plotselected
       * This not supported in flot 0.5.
       * @param {Ext.ux.Flot} this
       * @param {Object} event event object
       * @param {Object} range the rectangle ranges selected
       * @param {Object} item the items selected
       * The contents are same with plotselected
       */
      "plotselecting",
      /**
       * @event plothover
       * Fire when the mouse moves on Ext Flot canvas. 
       * If item is not null, the mouse moves on the item.
       * This event enables when grid.hovarable is true. 
       * If you return false, Ext.ux.Flot do nothing.
       * 'pos' contains the following members 
       * @param {Ext.ux.Flot} this
       * @param {Object} event event object
       * @param {Object} pos position of moving
       * {x: xpos, y: ypos, x2: xpos2, y2: ypos2}
       * @param {Object} item the items moved on
       * The contents are same with plotselected
       */
      "plothover",
      /**
       * @event plotclick
       * Fire when the mouse is clicked on Ext Flot canvas. 
       * If item is not null, the mouse clicks the item.
       * This event enables when grid.clickable is true. 
       * If you return false, Ext.ux.Flot do nothing.
       * @param {Ext.ux.Flot} this
       * @param {Object} event event object
       * @param {Object} pos position of clicking
       * {x: xpos, y: ypos, x2: xpos2, y2: ypos2}
       * @param {Object} item the items clicked
       * The contents are same with plotselected
       */
      "plotclick",
      /**
       * @event plotshow
       * Fires when the serie is shown.
       * @param {Ext.ux.Flot} this
       * @param {Object} series The serie shown
       */
      "plotshow",
      /**
       * @event plothide
       * Fires when the serie is hidden.
       * @param {Ext.ux.Flot} this
       * @param {Object} series The serie hidden
       */
      "plothide",
      /**
       * @event selectionactionchange
       * Fires when the selection.action is changed.
       * @param {Ext.ux.Flot} this
       * @param {String} action new selectin.action value
       */
      "selectionactionchange",
      /**
       * @event selectionchange
       * Fires when the any selections are changed
       * @param {Ext.ux.Flot} this
       * @param {Array} selected selected data points
       * It is same contents with this.getSelected()
       */
      "selectionchange",
      /**
       * @event legendclick
       * Fires when the legend is clicked
       * @param {Ext.ux.Flot} this
       * @param {Ext.Element} legend (legendColorBox ro legendLabel)
       * @param {Object} series the serie which is connected with the legend
       * If you return false, Ext.ux.Flot do nothing.
       */
      "legendclick");
  },

  /**
   * Convert the series data of flot to object for {@link Ext.data.JsonStore}. 
   * The return value can be read by Ext.data.JsonStore.loadData().
   * Its contents same format with HttpResponse. 
   * It includes 'metaData'. The data entity (root) is 'data'.
   * @param {Object} series The series to create data for Ext.data.JsonStore.
   * If you specify notihing, Ext.ux.Flot get them from getData()
   * @return {Object} Ext.data.JsonStore Object for loadData()
   */
  createStoreData: function(series) {
    series = series || this.getData();
    var axes = this.getAxes();
    var fields = [];
    var keys = ['xaxis', 'x2axis'];
    for (var k = 0; k < keys.length; k++) {
      fields.push({
        name: keys[k],
        xColumn: true,
        type: this.type,
        sortType: this.sortType
      });
    }
    var hash = {};
    for (var i = 0, len = series.length; i < len; i++) {
      var s = series[i];
      var name = s.label || i;
      var xaxis = (s.xaxis == axes.x2axis) ? 'x2axis' : 'xaxis';
      fields.push({ 
        name: name,
        type: this.type,
        sortType: this.sortType
      });

      for (var j = 0, dlen = s.data.length; j < dlen; j++) {
        var src  = s.data[j];
        if (src) {
          var dest = hash[src[0]] = hash[src[0]] || {};
          dest[xaxis] = src[0];
          dest[name]  = src[1];
        }
      }
    }
    var data = [];
    for (var key in hash) { data.push(hash[key]); }

    return {
      metaData: {
        root: 'data',
        totalProperty: 'total',
        successProperty: 'success',
        sortInfo: { field: 'xaxis', direction: 'ASC' },
        fields: fields
      },
      data:  data,
      total: data.length,
      success: true
    };
  },

  /**
   * Convert the data of {@link Ext.data.JsonStore} to for flot.
   * The each serie contains the following extensions for {@link Ext.data.JsonStore}.
   *  <li>dataIndex
   *  <li>type
   *  <li>sortType
   * @param {Ext.data.Store} store data store to use
   * If you specify nothing, this.store is used.
   * @param {String} xField The field name for x-axis 
   * It is the record member name for x-axis
   * If you specify nothing, store.xField is used.
   * @return {Array} data array which can be used by flot.
   */
  createSeries: function(store, xField) {
    store = store || this.store;
    if (typeof xField == 'undefined') { xField = store.xField; }
    var i, len;
    var series = [];
    for (i = 0, len = store.fields.keys.length; i < len; i++) {
      var finfo = store.fields.items[i];
      var idx   = finfo.dataIndex || finfo.name;
      if (xField == idx) { continue; }
      series.push({
        label:     finfo.name, 
        dataIndex: idx, 
        type:      this.type,
        sortType:  this.sortType,
        data: []
      });
    }
    store.each(function(rec) {
      var series = this.series;
      var store  = this.store;
      var x = rec.get(this.xField);
      for (var i = 0, len = series.length; i < len; i++) {
        var val = rec.get(series[i].dataIndex);
        series[i].data.push([x, val]);
      }
    }, { series: series, store: store, xField: xField });
    return series;
  },

  /**
   * Get the store which Ext.ux.Flot instance holds.
   * @return {Ext.data.JsonStore} JsonStore
   */
  getStore: function() {
    return this.store;
  },

  /**
   * Gather datapoints within range
   * @param {Object} ranges
   * ranges contain 'from' and 'to' in following members.
   * Note that the unit of 'from' and 'to' is same with each serie
   *  * xaxis yaxis x2axis y2axis
   *    * from to
   * @return {Array} datapoint within range of each serie
   */
  clipData: function(ranges) {
    var series = this.getData();
    var axes = this.getAxes();
    var clipped = [];
    for (var i = 0, len = series.length; i < len; i++) {
      var s = series[i];
      clipped[i] = {};
      clipped[i].series = s;
      clipped[i].datapoints = [];
      var xaxis = s.xaxis == axes.x2axis ? 'x2axis' : 'xaxis';
      var yaxis = s.yaxis == axes.y2axis ? 'y2axis' : 'yaxis';
      for (var j = 0, n = s.data.length; j < n; j++) {
        var d = s.data[j];
        if (d &&
            ranges[xaxis].from <= d[0] &&
            ranges[xaxis].to   >= d[0] &&
            ranges[yaxis].from <= d[1] &&
            ranges[yaxis].to   >= d[1]) {
          clipped[i].datapoints.push([d[0], d[1]]);
        }
      }
    }
    return clipped;
  },

  // private
  onRender: function(ct, position) {
    if (!this.template) {
      if (!Ext.ux.Flot.flotTemplate) {
        // 0: DOM ID for container
        Ext.ux.Flot.flotTemplate = new Ext.Template('<div id="{0}"></div>');
      }
      this.template = Ext.ux.Flot.flotTemplate;
    }
    var id = this.id || Ext.id(null, 'flot-container');
    var el, targs = [id];

    if (position) {
      el = this.template.insertBefore(position, targs, true);
      //ct = position;
    }else{
      el = this.template.append(ct, targs, true);
    }
    this.el = el;
    if (this.id) { this.el.dom.id = this.el.id = this.id; }
    this.el.setWidth( this.width  || ct.getWidth());
    this.el.setHeight(this.height || ct.getHeight());
    this.el.setStyle('cursor', this.selection.cursor[this.selection.action]);

    // draw el
    var series = this.series;
    if (this.data) { series = this.setupData(this.data, series); }
    if (series) {
      // Setup series and draw
      series = this.setupSeries(series);
      this.plot(series);

      // initliaze for hidden
      series = this.getData();
      for (var i = 0, len = series.length; i < len; i++) {
        var s = series[i];
        if (s.hidden) {
          s.hidden = !s.hidden;
          this.setHidden(s, !s.hidden);
        }
      }
    }
  },

  // private
  afterRender: function() {
    Ext.ux.Flot.superclass.afterRender.call(this);
    this.el.on({
      "mousedown":   this.onMouseDown,
      "mouseup":     this.onMouseUp,
      "mouseout":    this.onMouseOut,
      "click":       this.onClick,
      "dblclick":    this.onDblClick,
      "contextmenu": this.onContextMenu,
      scope: this
    });

    $('#' + this.id).bind('plotselected', function(event, range) {
      flot = Ext.getCmp(event.target.id);
      flot.onPlotSelected(event, range);
    });
    $('#' + this.id).bind('plotselecting', function(event, range) {
      flot = Ext.getCmp(event.target.id);
      flot.onPlotSelecting(event, range);
    });
    $('#' + this.id).bind('plothover', function(event, pos, item) {
      flot = Ext.getCmp(event.target.id);
      flot.onPlotHover(event, pos, item);
    });
    $('#' + this.id).bind('plotclick', function(event, pos, item) {
      flot = Ext.getCmp(event.target.id);
      flot.onPlotClick(event, pos, item);
    });

    this.updateAction();

    if (this.tooltip) {
      this.on(this.tooltipEvent, function(flot, event, pos, item) {
        if (item) { this.showTooltip(event, pos, item, false); }
      }, this);
    }
  },

  // private
  onResize: function(adjWidth, adjHeight, rawWidth, rawHeight) {
    //Ext.ux.Flot.superclass.onResize.call(this, adjWidth, adjHeight, rawWidth, rawHeight);
    this.el.setWidth(adjWidth);
    this.el.setHeight(adjHeight);
    try {
      this.plot(this.getData());
    } catch (e) {
      if (typeof e == 'string') {
        this.onResize.defer(200, this, [adjWidth, adjHeight, rawWidth, rawHeight]);
      } else {
        throw e;
      } 
    }
    this.syncSelected();
  },

  // private
  setupLegend: function() {
    // handle click of legend
    var legend_tbody = this.el.query("div.legend > table > tbody")[0];
    if (legend_tbody) {
      var series = this.getData();
      this.legendCmp = new Ext.Element(legend_tbody);
      this.legendEls = {};
      var color_boxes = this.legendCmp.query("tr > td.legendColorBox");
      var labels      = this.legendCmp.query("tr > td.legendLabel");
      for (var i = 0, len = series.length; i < len; i++) {
        var s = series[i];
        var idx = -1;
        for (var j = 0; j < labels.length; j++) {
          var text = labels[j].textContent || labels[j].innerHtml;
          if (text == s.label) { 
            idx = j; 
            break; 
          }
        }
        if (idx >= 0) {
          var cb = new Ext.Element(color_boxes[idx]);
          var lb = new Ext.Element(labels[idx]);
          cb.on('click', this.onLegendClick, this, {series: s});
          lb.on('click', this.onLegendClick, this, {series: s});
          var c = this.legendEls[s.label] || {};
          if (c.hidden != s.hidden) { (s.hidden) ? cb.fadeOut() : cb.fadeIn(); }
          if (s.hidden) { cb.hide(); }
          this.legendEls[s.label] = Ext.apply(c, {
            legendColorBox: cb, 
            legendLabel: lb, 
            series: s,
            hidden: s.hidden
          });
        }
      }
    }
  },

  // private
  onDraw: function() {
    this.setupLegend();
    this.store.loadData(this.createStoreData());
    if (!this.baseRanges) { this.baseRanges = this.getRanges(); }
    this.fireEvent('draw', this);
  },

  // private
  onSelectionChange: function() {
    this.updateAction();
    this.fireEvent('selectionchange', this, this.selected);
  },

  // private
  onLegendClick: function(e, legendDom, args) {
    var s = args.series;
    if (this.fireEvent('legendclick', this, Ext.get(legendDom), s) !== false) {
      this.setHidden(s, !s.hidden);
    }
  },

  // private
  onMouseDown: function(e) {
    this.lastEvent = this.mouseDownEvent = Ext.apply({}, e);
  },

  // private
  onMouseUp: function(e) {
    this.lastEvent = this.mouseUpEvent = Ext.apply({}, e);
  },

  // private
  onMouseOut: function(e) {
    this.lastEvent = this.mouseUpEvent = Ext.apply({}, e);
  },

  // private
  onClick: function(e) {
    this.fireEvent("click", this, e);
  },

  // private
  onDblClick: function(e) {
    if (this.fireEvent("dblclick", this, e) !== false) {
      if (this.selection.action == 'select') {
        this;   // nothing to do
      } else {  // zoom, move
        var applyRanges = this.getRanges();
        if (this.isSameRanges(applyRanges, this.baseRanges)) {
          if (this.currentRanges) { this.zoom(this.currentRanges); }
        } else {
          this.zoom(this.baseRanges);
        }
      }
    }
  },

  // private
  onContextMenu: function(e) {
    if (this.fireEvent("contextmenu", this, e) !== false) {
      var contextMenu = this.contextMenu;
      if (this.clickItem) {
        if (Math.abs(e.xy[0] - this.clickItem.pageX) <= 5 &&
            Math.abs(e.xy[1] - this.clickItem.pageY) <= 5) {
          contextMenu = this.datapointContextMenu || contextMenu;
        }
      }
      if (contextMenu) {
        var menu = new Ext.menu.Menu({ items: contextMenu });
        e.stopEvent();
        menu.showAt(e.getXY());
      }
    }
  },

  // private
  onPlotSelecting: function(event, ranges) {
    this.fireEvent('plotselecting', this, event, ranges);
  },

  // private
  onPlotSelected: function(event, ranges) {
    if (this.fireEvent('plotselected', this, event, ranges) !== false) {
      if (!this.mouseDownEvent || !this.mouseUpEvent) { return; }
      var diff_px = [ 
        this.mouseDownEvent.xy[0] - this.mouseUpEvent.xy[0],
        this.mouseDownEvent.xy[1] - this.mouseUpEvent.xy[1]
      ];
      var axes = this.getAxes();
      var r = {};
      var keys = ['xaxis', 'yaxis', 'x2axis', 'y2axis'], k, axis;

      switch (this.selection.action) {
        case 'select':
          if (!this.lastEvent[this.selection.appendKey]) {this.unselectAll();}
          var d = this.clipData(ranges);
          var changed = false;
          for (var i = 0, len = d.length; i < len; i++) {
            for (var j = 0, dlen = d[i].datapoints.length; j < dlen; j++) {
              if (this.addSelected(d[i].series, d[i].datapoints[j])) { changed = true; }
            }
          }
          if (changed) {this.onSelectionChange();}
          break;
        case 'zoom':
          var xmin, xmax, ymin, ymax;
          var x2min, x2max, y2min, y2max;
          var zoom = {}, zoomin, z;
          var w  = this.el.getWidth();
          var h  = this.el.getHeight();
          var rw = Math.abs(diff_px[0]);
          var rh = Math.abs(diff_px[1]);
          var fix_x = false, fix_y = false;
          switch (this.selection.zoomWindow) {
            case 'ranges': break;
            case 'expand': fix_x = (rw < rh); fix_y = (rw > rh); break;
            case 'shrink': fix_x = (rw > rh); fix_y = (rw < rh); break;
            case 'width':  fix_y = true; break;
            case 'height': fix_x = true; break;
            default: break; // ranges
          }
          for (k = 0; k < keys.length; k++) {
            axis = keys[k];
            if (!axes[axis].used) { 
              zoom[axis] = null;
              continue;
            } 
            zoom[axis] = z = {
              from:        ranges[axis].from,
              to:          ranges[axis].to,
              center:      (ranges[axis].from + ranges[axis].to) / 2,
              min:         axes[axis].min,
              max:         axes[axis].max,
              axisLength:  axes[axis].max - axes[axis].min,
              rangeLength: ranges[axis].to - ranges[axis].from
            };

            var scale = null;
            if        (axis[0] == 'x' && fix_x) {
              scale = rh / rw * w / h;
            } else if (axis[0] == 'y' && fix_y) {
              scale = rw / rh * h / w;
            }
            if (scale !== null) {
              z.fromOrg = z.from;
              z.toOrg   = z.to;
              z.from = z.center + (z.from - z.center) * scale;
              z.to   = z.center + (z.to   - z.center) * scale;
              z.rangeLength = z.to - z.from;
            } 
          }
          switch (this.selection.zoomDirection) {
            case 'tb': zoomin = diff_px[1] >= 0; break;
            case 'bt': zoomin = diff_px[1] <= 0; break;
            case 'lr': zoomin = diff_px[0] >= 0; break;
            case 'rl': zoomin = diff_px[0] <= 0; break;
            default:   zoomin = diff_px[1] >= 0; break; // tb
          }
          for (k = 0; k < keys.length; k++) {
            axis = keys[k];
            z = zoom[axis];
            if (!z) { continue; }
            if (zoomin) {
              r[axis] = { min: z.from, max: z.to };
            } else {
              r[axis] = {
                min: z.min + (z.min - z.from) * z.axisLength / z.rangeLength,
                max: z.max + (z.max - z.to)   * z.axisLength / z.rangeLength
              };
            }
          }
          this.zoom(r);
          break;
        case 'move':
          var to_left   = (diff_px[0] <= 0) ? true : false;
          var to_bottom = (diff_px[1] >= 0) ? true : false;
          for (k = 0; k < keys.length; k++) {
            axis = keys[k];
            if (!axes[axis].used) { continue; }
            var diff = ranges[axis].to  - ranges[axis].from;
            diff = ((axis[0] == 'x') ? to_left : to_bottom) ? -diff: diff;
            r[axis] = {
              min: axes[axis].min + diff, 
              max: axes[axis].max + diff
            };
          }
          this.zoom(r);
          break;
        default:
          break;
      }
    }
  },

  // private
  onPlotHover: function(event, pos, item)  {
    this.hoverItem = item;
    this.fireEvent('plothover', this, event, pos, item);
  },

  // private
  onPlotClick: function(event, pos, item)  {
    this.clickItem = item;
    if (this.fireEvent('plotclick', this, event, pos, item) !== false) {
      if (item) {
        if (item.series.selectable) {
          if (!this.lastEvent[this.selection.appendKey]) {this.unselectAll();}
          if (!this.addSelected(item.series, item.datapoint)) {
            this.removeSelected(item.series, item.datapoint);
          }
          this.onSelectionChange();
        }
      } else {
        if (!this.lastEvent[this.selection.appendKey]) { this.unselectAll(); }
      }
    }
  },

  /**
   * Set the action at range selection
   * @param {String} action 'select' or 'move' or 'zoom'
   */
  setSelectionAction: function(action) {
    this.selection.action = action;
    this.el.setStyle('cursor', this.selection.cursor[this.selection.action]);
    this.updateAction();
    this.fireEvent('selectionactionchange', this, action);
  },

  /**
   * Get current action of range selection
   * @return {String} 'select' or 'zoom' or 'move'
   */
  getSelectionAction: function() {
    return this.selection.action;
  },

  /**
   * Get current display range
   * @return range of display
   */
  getRanges: function() {
    var series = this.getData();
    var axes   = this.getAxes();
    var r = {};
    if (axes.xaxis)  { r.xaxis  = {min: axes.xaxis.min,  max: axes.xaxis.max};}
    if (axes.yaxis)  { r.yaxis  = {min: axes.yaxis.min,  max: axes.yaxis.max};}
    if (axes.x2axis) { r.x2axis = {min: axes.x2axis.min, max: axes.x2axis.max};}
    if (axes.y2axis) { r.y2axis = {min: axes.y2axis.min, max: axes.y2axis.max};}
    return r;
  },

  // private
  isSameRanges: function(ranges1, ranges2) {
    var keys = ['xaxis', 'yaxis', 'x2axis', 'y2axis'];
    for (var k = 0; k < keys.length; k++) {
      var key = keys[k];
      var r1 = ranges1[key], r2 = ranges2[key];
      if (r1.min != r2.min && r1.max != r2.max) { return false; }
    }
    return true;
  },

  /**
   * Set the new zooming range
   * @param {Object} range zooming range
   */
  zoom: function(ranges) {
    var keys = ['xaxis', 'yaxis', 'x2axis', 'y2axis'];
    for (var k = 0; k < keys.length; k++) {
      // from to -> min max
      var key = keys[k];
      var r = ranges[key];
      if (r) {
        if (typeof r.min == 'undefined') r.min = r.from;
        if (typeof r.max == 'undefined') r.max = r.to;
        Ext.apply(this[key], r);
      }
    }
    this.plot(this.getData());
    ranges = this.getRanges();
    if (!this.isSameRanges(ranges, this.baseRanges)) { this.currentRanges = ranges; }
  },

  /**
   * Zoom by ratio for aurrent dispaly range
   * @param {Number} ratio 1.0 means 100%.
   */
  zoomRatio: function(ratio) {
    var b = this.baseRanges;
    var r = {};
    if (b.xaxis)  { r.xaxis  = {min: b.xaxis.min  * ratio, max: b.xaxis.max  * ratio}; }
    if (b.yaxis)  { r.yaxis  = {min: b.yaxis.min  * ratio, max: b.yaxis.max  * ratio}; }
    if (b.x2axis) { r.x2axis = {min: b.x2axis.min * ratio, max: b.x2axis.max * ratio}; }
    if (b.y2axis) { r.y2axis = {min: b.y2axis.min * ratio, max: b.y2axis.max * ratio}; }
    this.zoom(r);
  },

  // private
  syncSelected: function() {
    for (var i = 0; i < this.selected.length; i++) {
      var selected = this.selected[i];
      selected.series = this.findSeries(selected.series.id);
      for (var j = 0; j < selected.datapoints.length; j++) {
        this.highlight(selected.series, selected.datapoints[j]);
      }
    }
  },

  // private
  addSelectedPoint: function(selected, datapoint) {
    i = selected.datapoints.indexOf(datapoint);
    if (i < 0) {
      selected.datapoints.push(datapoint);
      this.highlight(selected.series, datapoint);
      return true;
    }
    return false;
  },

  /**
   * Add a datapoint to selected datapoints
   * @param {Object} seris the owner serie of datapoint
   * @param {Object} datapoint datapoint to add
   * @return {Boolean} really the datapoint is added
   */
  addSelected: function(series, datapoint) {
    if (!this.selection || !series.selectable) {return false;}
    var selected = null, i, len;
    for (i = 0, len = this.selected.length; i < len; i++) {
      if (this.selected[i].series == series) { 
        selected = this.selected[i];
        break; 
      }
    }
    if (!selected) { 
      selected = {series: series, datapoints: []};
      this.selected.push(selected); 
    }

    return this.addSelectedPoint(selected, datapoint);
  },

  /**
   * Select all datapoints in the serie
   * @param {String/Object} _series the serie to select all datapoints
   * If you specify nothing, all series are selected.
   */
  selectAll: function(_series) {
    if (!this.selection) { return; }
    if (typeof _series == 'string') { _series = this.findSeries(_series); }
    var changed = false;
    var series = this.getData();
    this.selected = [];
    for (var i = 0, len = series.length; i < len; i++) {
      if (typeof _series != 'undefined' && _series != series[i]) { continue; }
      if (!series[i].selectable) { continue; }
      var selected = {series: series[i], datapoints: []};
      this.selected.push(selected);
      for (var j = 0, dlen = series[i].data.length; j < dlen; j++) {
        if (this.addSelectedPoint(selected, series[i].data[j])) {
          changed = true;
        }
      }
    }
    if (changed) { this.onSelectionChange(); }
  },

  /**
   * Remove a datapoint from selected datapoints.
   * @param {Object} seris the owner serie of datapoint to remove
   * @param {Object} datapoint datapoint to remove
   */
  removeSelected: function(series, datapoint) {
    for (var i = 0, len = this.selected.length; i < len; i++) {
      var s = this.selected[i];
      if (s.series == series) { 
        this.unhighlight(series, datapoint);
        s.datapoints.remove(datapoint);
        break; 
      }
    }
  },

  /**
   * Unselect current selection
   * @param {String/Object} _series
   */
  unselectAll: function(_series) {
    var changed = false;
    if (typeof _series == 'string') { _series = this.findSeries(_series); }
    for (var i = 0, len = this.selected.length; i < len; i++) {
      var s = this.selected[i];
      if (typeof _series != 'undefined' && _series != s.series) { continue; }
      for (var j = 0, dlen = s.datapoints.length; j < dlen; j++) {
        this.unhighlight(s.series, s.datapoints[j]);
      }
      changed = true;
      s.datapoints = [];
    }
    if (changed) { this.onSelectionChange(); }
  },

  /**
   * Return the information of selected datapoints by Array
   * The Array contain series and datapoints
<pre>
[{
  series: <series>
  datapoints: [[<x>, <y>], ...]
}, ...]
</pre>
   * @return {Array} selected datapoints information
   */
  getSelected: function() {
    return this.selected;
  },

  /**
   * Create {@link Ext.data.Record} from selected datapoints 
   * @param {Object} selected datapoints are got by getSelected()
   * @return {Array} datapoints by {@link Ext.data.Record}
   */
  getSelectedRecords: function(selected) {
    var records = [];
    selected = selected || this.getSelected();
    for (var i = 0, len = selected.length; i < len; i++) {
      for (var j = 0, dlen = selected[i].datapoints.length; j < dlen; j++) {
        var dp = selected[i].datapoints[j];
        var xkey = selected[i].series.x2axis ? 'x2axis': 'xaxis';
        var idx = this.store.find(xkey, dp[0]);
        records.push(this.store.getAt(idx));
      }
    }
    return records;
  },

  // private
  setActionDisabled: function(key, disabled) {
    if (this.actions[key]) { this.actions[key].setDisabled(disabled); }
  },

  // private
  updateAction: function() {
    this.setActionDisabled('zoom',   this.selection.action === 'zoom');
    this.setActionDisabled('select', this.selection.action === 'select');
    this.setActionDisabled('move',   this.selection.action === 'move');
    var n_selected = 0, i, len;
    for (i = 0, len = this.selected.length; i < len; i++) {
      n_selected += this.selected[i].datapoints.length;
    }
    this.setActionDisabled('unselectall', this.selected.length === 0 || n_selected === 0);
    this.setActionDisabled('property',   !this.hasProperty());
    var item = this.clickItem || this.hoverItem;
    if (item) {
      n_selected = 0;
      for (i = 0, len = this.selected.length; i < len; i++) {
        if (this.selected[i].series == item.series) {
          n_selected = this.selected[i].datapoints.length;
          break;
        }
      }
      this.setActionDisabled('selectalldatapoint',   !item.series);
      this.setActionDisabled('unselectalldatapoint', !item.series || n_selected === 0);
      this.setActionDisabled('showseries',           !item.series.hidden);
      this.setActionDisabled('hideseries',           item.series.hidden);
    }
  },

  // private
  hasProperty: function() {
    return true;
  },

  // private
  showProperty: function() {
    if (!this.propertyCmp) {
      // Create a window
      this.propertyCmp = new Ext.Window({
        closeAction: 'hide',
        layout: 'fit',
        width: 400,
        height: 300,
        items: [{
          xtype: 'flotpropertygrid',
          flot: this,
          layout: 'fit'
        }]
      });
      // binding
      var grid = this.propertyCmp.findByType('flotpropertygrid')[0];
      this.bindGrid(grid);
    }
    this.propertyCmp.show();
  },

  /**
   * Relate Ext.ux.Flot and Ext.grid.GridPanel
   * @param {Ext.grid.GridPanel} grid grid to relate with Ext.ux.Flot instance
   */
  bindGrid: function(grid) {
    this.on('selectionchange', function(flot, selected) {
      var records = flot.getSelectedRecords(selected);
      var cm = this.getColumnModel();
      var sm = this.getSelectionModel();
      for (var i = 0, len = records.length; i < len; i++) {
        var rec = records[i];
        var x = this.store.indexOf(rec);
        for (var key in rec.data) {
          if (typeof rec.data.key != "undefined") {
            var y = cm.findColumnIndex(key);
            sm.select(x, y);
          }
        }
      }
    }, grid);
    grid.getSelectionModel().on('selectionchange', function(sm) {
    }, this);
  },

  // private
  showTooltip: function(event, pos, item, forceUpdate) {
    if (!this.tooltip || this.disableTooltip) { return null; }
    if (!forceUpdate && this.prevTooltipItem && 
        this.prevTooltipItem.datapoint[0] == item.datapoint[0] &&
        this.prevTooltipItem.datapoint[1] == item.datapoint[1] &&
        this.prevTooltipItem.series       == item.series) {
      return null;
    }
    this.clearTooltip(this.tooltipCmp);
    this.prevTooltipItem = item;

    var s = item.series;
    var axes = this.getAxes();
    var xaxis = (s.xaxis) ? s.xaxis : s.x2axis;
    var yaxis = (s.yaxis) ? s.yaxis : s.y2axis;
    var dp = [];
    axes = [xaxis, yaxis];
    for (var i = 0; i < 2; i++) {
      try {
        dp[i] = axes[i].tickFormatter(item.datapoint[i], axes[i]);
      } catch(e) {
        dp[i] = item.datapoint[i];
      }
    }
    var o = {
      tipId:       event.target.id + '-tip',
      pageX:       pos.pageX,
      pageY:       pos.pageY,
      x:           pos.x,
      y:           pos.y,
      0:           dp[0],
      1:           dp[1],
      datapointX:  item.datapoint[0],
      datapointY:  item.datapoint[1],
      label:       item.series.label,
      color:       item.series.color,
      shadowSize:  item.series.shadowSize,
      dataIndex:   item.dataIndex,
      seriesIndex: item.seriesIndex,
      series:      item.series
    };

    var c = {
      renderTo: Ext.getBody(),
      targetXY: [pos.pageX, pos.pageY]
    };
    var tooltip = this.tooltip;
    if (typeof tooltip == 'boolean') { 
      tooltip = '<div id="{tipId}">{label} ({0}, {1})</div>'; 
    }
    if (typeof tooltip == 'string') { 
      if (!this.tipTemplate) {
        this.tipTemplate = new Ext.XTemplate(tooltip);
      }
      c.html = this.tipTemplate.apply(o);
    } else if (typeof tooltip == 'object') { 
      Ext.apply(c, this.tooltip); 
    } else if (typeof tooltip == 'function') {
      c.html = tooltip.call(this, o);
    }
    this.tooltipCmp = new Ext.ToolTip(c);
    this.tooltipCmp.show();
    this.tooltipCmp.on('hide', function(tooltipCmp) {
      this.clearTooltip(tooltipCmp);
    }, this);
    return this.tooltipCmp;
  },

  // private
  clearTooltip: function(tooltipCmp) {
    tooltipCmp = tooltipCmp || this.tooltipCmp;
    if (!tooltipCmp) { return; }
    this.prevTooltipItem = null;
    if (tooltipCmp == this.tooltipCmp) { this.tooltipCmp = null; }
    tooltipCmp.destroy();
  },

  /**
   * Enable/disable the tooltip
   * @param {Bool} disable false=enable true=disable
   */
  setTooltipDisable: function(disable) {
    this.disableTooltip = disable;
  },

  /**
   * Search a serie
   * @param {String} name serie name to find
   * @return {Object} found serie (null means not found)
   */
  findSeries: function(name) {
    var series = this.getData();
    for (var i = 0, len = series.length; i < len; i++) {
      var idx = series[i].dataIndex || series[i].label;
      if (name === idx || name === series[i].id) { return series[i]; }
    }
    return null;
  },

  // private
  setupSeries: function(series) {
    if (typeof series.length == 'undefined') {series = [series];}
    for (var i = 0, len = series.length; i < len; i++) {
      var s = series[i];
      if (typeof s.length != 'undefined') {s = series[i] = {data: s};}
      // apply baseSeries
      Ext.apply(s, this.baseSeries);
      // always create 'legend' 'lines' 'points' 'bars' 'pies'
      Ext.applyIf(s, {
        id: Ext.id(null, 'flot-series'),
        /*
        lines:  Ext.apply({}, s.lines),
        points: Ext.apply({}, s.points),
        bars:   Ext.apply({}, s.bars),
        pies:   Ext.apply({}, s.pies),
        */
        legend: Ext.apply({}, s.legend),
        selectable: true,
        hidden: false
      });
    }
    return series;
  },

  /**
   * Call plot method of flot
   * @param {Array} series series to plot
   */
  plot: function(series) {
    // duplicate the series to redraw
    var _series = [];
    for (var i = 0, len = series.length; i < len; i++) {
      _series.push(Ext.apply({}, series[i]));
      if (this.flot) {
        // when redraw, replace axes value to number again
        var axes = this.getAxes();
        var s = _series[i];
        if (s.xaxis && typeof s.xaxis != 'number') {
          s.xaxis = (s.xaxis == axes.x2axis) ? '2' : '1';
        }
        if (s.yaxis && typeof s.yaxis != 'number') {
          s.yaxis = (s.yaxis == axes.y2axis) ? '2' : '1';
        }
      }
    }
    if (this.fireEvent('beforedraw', this, _series) !== false) {
      this.flot = $.plot($('#' + this.id), _series, this);
      this.onDraw();
    }
  },

  /**
   * Insert a new serie to position specified by idx
   * @param {Object} series the serie to insert
   * @param {Number} idx position to insert
   */
  insertSeries: function(series, idx) {
    var _series;
    _series = (this.flot) ? this.getData() : [];
    if (idx < 0) { idx = _series.length; }
    _series.splice(idx, 0, series);
    _series = this.setupSeries(_series);
    // FIXME Reset color configuration by default
    for (i = 0; i < _series.length; i++) { delete _series[i].color; }
    if (this.flot) {
      this.setData(_series);
      this.redraw();
    } else {
      this.series = _series;
    }
  },

  /**
   * Insert a new serie into the top of series
   * @param {Object} series the serie to insert
   */
  prependSeries: function(series) {
    this.insertSeries(series, 0);
  },

  /**
   * Insert a new serie into the bottom of series
   * @param {Object} series the serie to insert
   */
  appendSeries: function(series) {
    this.insertSeries(series, -1);
  },

  /**
   * Insert a new serie that built from data into the current series array
   * @param {Object/Array} data serie data to insert
   * @param {Object} series base serie options to pass setupData() 
   * @param {Number} idx position to insert
   */
  insertData: function(data, series, idx) {
    var _series = this.setupData(data, series);
    for (var i = 0; i < _series.length; i++) {
      this.insertSeries(series[i], (idx < 0) ? idx : idx+i);
    }
  },

  /**
   * Insert a new serie that built from data into top of series array
   * @param {Object/Array} data serie data to insert
   * @param {Object} series base serie options to pass setupData() 
   */
  prependData: function(data, series) {
    this.insertData(data, series, 0);
  },

  /**
   * Insert a new serie that built from data into bottom of series array
   * @param {Object/Array} data serie data to insert
   * @param {Object} series base serie options to pass setupData() 
   */
  appendData: function(data, series) {
    this.insertData(data, series, -1);
  },

  // private
  redraw: function() {
    var series = this.getData();
    if (this.fireEvent('beforedraw', this, series) !== false) {
      this.setupGrid();
      this.draw();
      this.onDraw();
    }
  },

  /**
   * Change the show/hidden property of the serie
   * @param {String/Object} series the serie to show or hide
   * @param {Bool} hidden true=hide false=show
   */
  setHidden: function(series, hidden) {
    var s = (typeof series == 'string') ? this.findSeries(series) : series;
    if (s.hidable === false) { return; }
    var keys = ['lines', 'points', 'bars', 'pies'];
    if (s.hidden != hidden) {
      s.hidden = hidden;
      for (var k = 0, len = keys.length; k < len; k++) {
        var key = keys[k];
        if (hidden) {
          s[key + 'Show'] = s[key];
          s[key] = Ext.applyIf({show: false, lineWidth: 0, fill: 0}, s[key]);
        } else {
          s[key] = s[key + 'Show'] || s[key];
        }
      }
      if (hidden) {
        s.colorShow  = s.color;
        s.color      = this.grid.backgroundColor || "#ffffff";
        s.shadowSizeShow = s.shadowSize;
        s.shadowSize = 0;
      } else {
        s.color      = s.colorShow;
        s.shadowSize = s.shadowSizeShow;
      }
      this.redraw();
      this.updateAction();
      this.fireEvent(hidden ? 'plothide' : 'plotshow', this, series);
    }
  },

  /**
   * Wrapper of flot setSelection 
   *<br><br>
   * Set the selection rectangle. 
   * The passed in ranges is on the same form as returned in the "plotselected" event. 
   * If the selection mode is "x", you should put in either an xaxis (or x2axis) object,
   * if the mode is "y" you need to put in an yaxis (or y2axis) object
   * and both xaxis/x2axis and yaxis/y2axis if the selection mode is "xy", like this:
<pre>
setSelection({ xaxis: { from: 0, to: 10 }, yaxis: { from: 40, to: 60 } });
</pre>
   * setSelection will trigger the "plotselected" event when called. If
   * you don't want that to happen, e.g. if you're inside a
   * "plotselected" handler, pass true as the second parameter.
   * @param {Object}  ranges reclangle range to select
   */
  setSelection: function(ranges, preventEvent) {
    return this.flot.setSelection(ranges, preventEvent);
  },
  /**
   * Wrapper of flot clearSelection
   *
   * Clear the selection rectangle. Pass in true to avoid getting a "plotunselected" event.
   */
  clearSelection: function() {
    return this.flot.clearSelection();
  },
  /**
   * Wrapper of flot setCrosshair
   * This is not supported in flot 0.5.
   *<br><br>
   * Set the position of the crosshair. 
   * Note that this is cleared if the user moves the mouse. 
   * "pos" should be on the form { x: xpos, y: ypos } (or x2 and y2 if you're using the secondary axes), 
   * which is coincidentally the same format as what you get from a "plothover" event. 
   * If "pos" is null, the crosshair is cleared.
   * @param {Object}
   */
  setCrosshair: function(pos) {
    return this.flot.setCrosshair(pos);
  },
  /**
   * Wrapper of flot clearCrosshair 
   * This is not supported in flot 0.5.
   *<br><br>
   * Clear the crosshair.
   */
  clearCrosshair: function() {
    return this.flot.clearCrosshair();
  },
  /**
   * Wrapper of flot highlight 
   *<br><br>
   * Highlight a specific datapoint in the data series. 
   * You can either specify the actual objects, e.g. 
   * if you got them from a "plotclick" event, or you can specify the indices, e.g.
   * highlight(1, 3) to highlight the fourth point in the second series.
   * @param {Nmuber) series index
   * @param {Number} datapoint index
   */
  highlight: function(series, datapoint) {
    return this.flot.highlight(series, datapoint);
  },
  /**
   * Wrapper of flot unhighlight 
   *<br><br>
   * Remove the highlighting of the point, same parameters as highlight.
   * @param {Number} target serie
   * @param {Number} datapoint to unhighlight
   */
  unhighlight: function(series, datapoint) {
    return this.flot.unhighlight(series, datapoint);
  },
  /**
   * Wrapper of flot setData
   *<br><br>
   * You can use this to reset the data used. Note that axis scaling, ticks, legend etc. 
   * will not be recomputed (use setupGrid() to do that). 
   * You'll probably want to call draw() afterwards.
   *<br><br>
   * You can use this function to speed up redrawing a plot if you know
   * that the axes won't change. Put in the new data with
   * setData(newdata) and call draw() afterwards, and you're good to go.
   * @param {Array} Series to set
   */
  setData: function(series) {
    return this.flot.setData(series);
  },
  /**
   * Wrapper of flot setupGrid
   *<br><br>
   * Recalculate and set axis scaling, ticks, legend etc.
   *<br><br>
   * Note that because of the drawing model of the canvas, 
   * this function will immediately redraw (actually reinsert in the DOM)
   * the labels and the legend, but not the actual tick lines because they're drawn on the canvas. 
   * You need to call draw() to get the canvas redrawn.
   */
  setupGrid: function() {
    return this.flot.setupGrid();
  },
  /**
   * Wrapper of flot draw
   *<br><br>
   * Redraws the canvas.
   */
  draw: function() {
    return this.flot.draw();
  },
  /**
   * Wrapper of flot getData
   *<br><br>
   * Returns an array of the data series currently used on normalized
   * form with missing settings filled in according to the global
   * options. So for instance to find out what color Flot has assigned
   * to the data series, you could do this:
<pre>
var series = plot.getData();
for (var i = 0; i < series.length; ++i)
  alert(series[i].color);
</pre>
   * @return {Array} current series Array which the Ext.ux.Flot instance holds
   */
  getData: function() {
    return (this.flot) ? this.flot.getData() : this.series;
  },
  /**
   * Wrapper of flot getAxes 
   *<br><br>
   * Gets an object with the axes settings as { xaxis, yaxis, x2axis, y2axis }. 
   * Various things are stuffed inside an axis object, e.g.
   * you could use getAxes().xaxis.ticks to find out what the ticks are for the xaxis.
   * @return {Object} axis informations (xaxis yaxis x2axis y2axis)
   */
  getAxes: function() {
    return this.flot.getAxes();
  },
  /**
   * Wrapper of flot getCanvas 
   *<br><br>
   * Returns the canvas used for drawing in case you need to hack on it yourself. 
   * You'll probably need to get the plot offset too.
   * @return {Object} canvas
   */
  getCanvas: function() {
    return this.flot.getCanvas();
  },
  /**
   * Wrapper of flot getPlotOffset 
   *<br><br>
   * Gets the offset that the grid has within the canvas as an object
   * with distances from the canvas edges as "left", "right", "top", "bottom". 
   * I.e., if you draw a circle on the canvas with the center placed at (left, top), 
   * its center will be at the top-most, left corner of the grid.
   * @return {Object} offset informations of plotting area (left, bottom, right, top)
   */
  getPlotOffset: function() {
    return this.flot.getPlotOffset();
  }
});
Ext.reg('flot', Ext.ux.Flot);

/**
 * @class Ext.ux.Flot.grid
 * @singleton
 * Methods for grid of flot
 * Note that it does not means Ext.grid.
 */
Ext.ns('Ext.ux.Flot.grid');

/**
 * Templates for marking of week-end.
 * Typically, set it to grid.markings.
 * Now, it supports just for xaxis
<pre>
grid: { markings: Ext.ux.Flot.grid.weekendMarkings }
</pre>
 * @param {Object} axes setting for axis
 * @return {Array} marking area  by Array 
 * TODO yaxis x2axis y2axis are not supported.
 * @member Ext.ux.Flot.grid
 * @method weekendMarkings
 */
Ext.ux.Flot.grid.weekendMarkings = function(axes) {
  var markings = [];
  var d = new Date(axes.xaxis.min);
  // go to the first Saturday
  d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 1) % 7));
  d.setUTCSeconds(0);
  d.setUTCMinutes(0);
  d.setUTCHours(0);
  var i = d.getTime();
  do {
    // when we don't set yaxis the rectangle automatically
    // extends to infinity upwards and downwards
    markings.push({ xaxis: { from: i, to: i + 2 * 24 * 60 * 60 * 1000 } });
    i += 7 * 24 * 60 * 60 * 1000;
  } while (i < axes.xaxis.max);

  return markings;
};

/**
 * @class Ext.ux.FlotPropertyGrid
 * @extends Ext.grid.GridPanel
 * Standard GridPanel for Ext.ux.Flot
 * It dispalys the data which is set in Ext.ux.Flot.store 
 * @constructor
 * @param {Object} config configuration object
 */
Ext.ux.FlotPropertyGrid = Ext.extend(Ext.grid.GridPanel, {
  // private
  initComponent: function() {
    var cm = [{
      header:    'X',
      dataIndex: 'xaxis',
      sortable:  true
    }, {
      header:    'X2',
      dataIndex: 'x2axis',
      hidden:    true,
      sortable:  true
    }];
    var series = this.flot.getData();
    for (var i = 0, len = series.length; i < len; i++) {
      var s = series[i];
      var renderer = function(value, cell, rec) {
        cell.css = 'background: ' + s.color;
        return value;
      };
      var c = {
        header:    s.label || _('Series') + ' ' + i,
        dataIndex: s.label || i,
        hidden:    s.hidden,
        renderer:  renderer,
        sortable:  true
      };
      cm.push(Ext.apply(c, this.basePropertyColumn));
    }

    Ext.applyIf(this, {
      border: false,
      store: this.flot.getStore(),
      cm: new Ext.grid.ColumnModel(cm),
      sm: new Ext.grid.CellSelectionModel({
        singleSelect: false
      }),
      viewConfig: {
        //columnsText: _('Columns'),
        emptyText: _('No Data')
      }
    });
    Ext.ux.FlotPropertyGrid.superclass.initComponent.call(this);
  }
});
Ext.reg('flotpropertygrid', Ext.ux.FlotPropertyGrid);
