/* $Id: GetText.js 3825 2009-05-26 09:37:56Z suzuki $
 * vim:sw=2:ts=8:sts=2:et:ft=javascript
 *
 * 以下から拝借して、prototype.js 依存から Ext 依存にしました。
 * http://blog.bz2.jp/archives/2006/05/javascript-5.html 
 *
 * ただし、bindTextDomain を使用してサーバから動的に取得せず、
 * 直接 <domain>.js をインクルードし setText を用いる場合は、
 * Ext は必要ありません。
 */

/**
 * @class Locale
 * ロケールを管理するオブジェクト
 * 一度に 1 つの言語しか使用できません。
 * @singleton
 * @constructor
 */
Locale = new (function() {

  this.messages = {};

  /**
   * ロケールハッシュに登録する
   * 同一のキーワードがあった場合は、上書きされます。
   * 通常は <pre><locale>/LC_MESSAGES/<domain>.js</pre> 内で呼び出されます。
   * @param {String} locale_array [[<en>, <locale_text>], ...] の配列
   * @param {String/Array} locale セットする言語
   * @return {Bool} 登録されたか
   */
  this.setText = function(locale_array, locale) {
    var lang = navigator.language || navigator.userLanguage || navigator.systemLanguage;
    if (typeof locale == "string") { locale = locale.split(','); }
    if (typeof locale != "undefined" && typeof locale.indexOf == "function" && locale.indexOf(lang) < 0) { return false; }
    for (var i = 0, len = locale_array.length; i < len; i++) {
      var loc = locale_array[i];
      this.messages[loc[0]] = loc[1];
    }
    return true;
  };

  /**
   * 翻訳する
   * ハッシュを引くだけです。
   * @param {String} str 翻訳前文字列
   * @return {String} 翻訳後文字列
   */
  this.getText = function(str) {
    return this.messages[str] || str;
  };

  /**
   * キーワード登録する
   * gettext コンパイル時にのみ用い、実際の翻訳は getText にて行われます。
   * @param {String} str GetText に登録するキーワード
   * @return {String} 登録されたキーワード
   */
  this.getTextNoop = function(str) {
    return str;
  };
})();

/**
 * 一般的な gettext のエイリアス
 * 翻訳する。
 * @param {String} 翻訳前文字列
 * @return {String} 翻訳後文字列
 */
_ = function(str) { return Locale.getText(str); };

/**
 * 一般的な gettext のエイリアス
 * 翻訳キーワードを定義するだけ、翻訳そのものはしない。
 * @param {String} 登録するキーワード
 * @return {String} 登録後キーワード
 */
N_ = function(str) { return Locale.getTextNoop(str); };
