/* $Id: admin.js 2310 2008-10-10 08:55:17Z suzuki $
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 */

/**
 * @class Csv
 * CSV ライブラリ
 * @singleton
 */
if (typeof Csv == 'undefined') { Csv = {}; }
/**
 * CSV parser.
 * 
 * result of this function can be used like "csv[row][col]".
 * all rows has the same number of columns.
 * 
 * @param {String} src raw string of CSV format
 * @return {Array} an Array(2D)
 */
Csv.parse = function(src) {

  // constants
  var QUOT = '"', SEP = ',', CR = "\r", LF = "\n";

  // data to be generated
  var sheet = [], row = [], cell = "";

  // status flags
  var inquot = false;      // true when the current cell starts with quot.
  var cn = src.charAt(0);  // the next character, to be the 1st one before scanning.

  for (var i = 0; i < src.length; i++) {
    var cc = cn;  // current character is the next character of previous loop.
    cn = (i == src.length - 1) ? null : src.charAt(i + 1); // the next character

    if (cc == CR) {
      if (cn != LF) cc = LF;    // CR without LF : considerd as LF
      if (cn == LF) continue;   // CR with LF : skip this CR
    }

    if (inquot) {
      // put a character to current cell with quot character escape if ...
      // current cell starts with quot and
      // now quoted string is still not terminated.
      // - double quot: puts a quot, then progress cursor twice.
      // - single quot: ends this mode.
      // - else       : put a character to current cell.
      switch(cc) {
        case QUOT:
          if (cn == QUOT) { cell += QUOT; i++; }
          else inquot = false; 
          break;
        default:
          cell += cc;
          break;
      }
    }
    else {
      // put a character to current cell or move to the next cell/row if ...
      // current cell does still not start,
      // starts without quot or 
      // quot terminated in cell.
      // - newline  : ends current row.
      // - comma    : ends current cell.
      // - 1st quot : starts quoted cell. (it would be happen with the 1st character of cell.)
      // - else     : put a character to current cell.
      switch(cc) {
        case LF:
          row.push(cell); cell = "";
          sheet.push(row); row = []; 
          break;
        case SEP:
          row.push(cell); cell = ""; 
          break;
        case QUOT:
          if (cell === "") { 
            inquot = true; 
            break; 
          }
          /*FALLTHROUGTH*/
        default:
          cell += cc;
          break;
      }
    }
  }

  // join characters after the last spearator to this sheet.
  if(cell !== "") row.push(cell);
  if(row.length > 0) sheet.push(row);

  // adjust number of columns of each rows.
  var cols = 0; // the max length of each row
  for (i = 0; i < sheet.length; i++) {
    cols = Math.max(sheet[i].length, cols);
  }
  for (i = 0; i < sheet.length; i++) {
    var pad = cols - sheet[i].length; // count to be padded.
    for (j = 0; j < pad; j++) {
      sheet[i].push("");
    }
  }

  return sheet;
};

