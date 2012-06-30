(function() {
    AP = {};

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
