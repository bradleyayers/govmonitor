var com;
if (!com) {
    com = {};
} else if (typeof com != "object") {
    throw new Error("com exists and is not an object.");
}

if (!com.chrisdoble) {
    com.chrisdoble = {};
} else if (typeof com.chrisdoble != "object"){
    throw new Error("com.chrisdoble exists and is not an object.");
}

// Add an initialiser.
com.chrisdoble.addInitialiser = function(initialiser) {
    if (!com.chrisdoble.initialisers) {
        com.chrisdoble.initialisers = [];
    }

    com.chrisdoble.initialisers.push(initialiser);
}

// Run all registered initialisers.
com.chrisdoble.initialise = function() {
    for (var i in com.chrisdoble.initialisers) {
        com.chrisdoble.initialisers[i]();
    }
}

jQuery(document).ready(function($) {
    // Pass a CSRF token in AJAX requests.
    $(document).ajaxSend(function(event, request, settings) {
        var methods = /^(GET|HEAD|OPTIONS|TRACE)$/;
        if (!methods.test(settings.type) && !settings.crossDomain) {
            request.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
        }
    });

    com.chrisdoble.initialise();
});
