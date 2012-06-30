(function() {
  AP = {};

  /**
   * Shows a tooltip attached to the given element prompting the user to log in.
   * A one-shot click handler is attached to the document to close the tooltip.
   */
  AP.showLogInTooltip = function(el, options) {
    var defaults = {
      trigger: "manual",
      placement: "bottom",
      title: function() {
        var path = window.location.pathname + window.location.search;
        return "You must <a href='/login?next=" + path + "'>log in</a> to " +
            (options.verb || "do that") + "!";
      }
    };

    $(el).tooltip($.extend({}, defaults, options)).tooltip("show");
    $(document).one("click", function() { $(el).tooltip("hide"); });
  };

  /**
   * Returns the content of the meta tag with the given name.
   */
  AP.meta = function(name) {
    return $("meta[name=" + name +"]").attr("content");
  };

  /**
   * Ensures that a namespace exists, creating it if necessary.
   *
   * @param name A dot-separated package name (e.g. AP.Package).
   */
  AP.namespace = function(name) {
    var container = window;
    _.each(name.split("."), function(bit) {
      container = container[bit] || (container[bit] = {});
    });
  };

  // Include a CSRF token in all AJAX requests.
  $(document).ajaxSend(function(e, request, settings) {
    var methods = /^(GET|HEAD|OPTIONS|TRACE)$/;
    if (!methods.test(settings.type) && !settings.crossDomain) {
      request.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
    }
  });
})();
