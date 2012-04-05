jQuery(function($) {
    // Pass a CSRF token in AJAX requests.
    $(document).ajaxSend(function(event, request, settings) {
        var methods = /^(GET|HEAD|OPTIONS|TRACE)$/;
        if (!methods.test(settings.type) && !settings.crossDomain) {
            request.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
        }
    });
});
