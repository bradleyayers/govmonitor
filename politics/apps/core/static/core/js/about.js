jQuery(function($) {
    if (!$("html").hasClass("about")) {
        return;
    }

    function highlightQuestion(id) {
        var question = $("ol.questions " + id);

        if (question.length) {
            $("ol.questions li").removeClass("highlighted");
            question.addClass("highlighted");
        }
    }

    $("a").click(function() {
        var target = $(this).attr("href");
        if (target.charAt(0) == "#") {
            highlightQuestion(target);
        }
    });

    highlightQuestion(window.location.hash);
});
