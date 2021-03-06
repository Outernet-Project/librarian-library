// Generated by CoffeeScript 1.10.0
var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

(function(window, $, templates) {
  var contentLanguage, getLocalePrefix, getOpenerParams, getOpenerUrl, libraryItemLinkSelector, libraryList, openerPanelSelector;
  libraryList = $('#library-list');
  libraryItemLinkSelector = '.library-item-link';
  openerPanelSelector = '#content';
  contentLanguage = $('.library-filterbar #language');
  $('#content-language').on('change', function() {
    $(this).parents('form').submit();
  });
  getLocalePrefix = function() {
    return window.location.pathname.split('/')[1];
  };
  getOpenerUrl = function(targetCtype, path) {
    path = encodeURIComponent(path);
    return "/" + (getLocalePrefix()) + "/openers/" + targetCtype + "/?path=" + path;
  };
  getOpenerParams = function(link) {
    var ctypes, path, preferredType, targetCtype;
    ctypes = link.data('ctypes').split(',');
    preferredType = link.data('preferred-ctype');
    path = link.data('path');
    if (!ctypes.length) {
      ctypes.push('generic');
    }
    targetCtype = indexOf.call(ctypes, preferredType) >= 0 ? preferredType : ctypes[0];
    return {
      path: path,
      targetCtype: targetCtype
    };
  };
  libraryList.on('click', libraryItemLinkSelector, function(e) {
    var link, path, ref, targetCtype, url;
    link = $(this);
    ref = getOpenerParams(link), path = ref.path, targetCtype = ref.targetCtype;
    if (targetCtype === 'generic') {
      return;
    }
    e.preventDefault();
    url = getOpenerUrl(targetCtype, path);
    console.log(url);
    $.modalContent(url, {
      fullScreen: true
    });
  });
  return contentLanguage.on('change', function(e) {
    var form, select;
    select = $(this);
    form = select.parents('form');
    return form.submit();
  });
})(this, this.jQuery, this.templates);
