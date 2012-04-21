/**
 * Highlights the selected question on the about page.
 */
$(function() {
    // Don't bother if we're not on the about page.
    if (!$("html").hasClass("about")) {
        return;
    }

    var highlightQuestion = function(id) {
        $("ol.questions li").removeClass("highlighted");
        $("ol.questions " + id).addClass("highlighted");
    }

    $("a").click(function() {
        var target = $(this).attr("href");
        if (target.charAt(0) == "#") {
            highlightQuestion(target);
        }
    });

    highlightQuestion(window.location.hash);
});
