$(function() {
    if (!$("html").is(".faq")) {
        return;
    }

    // Highlight the question with the given id.
    var highlightQuestion = function(id) {
        $("ol.questions li").removeClass("highlighted");
        $("ol.questions " + id).addClass("highlighted");
    }

    $(document).on("click", "a", function() {
        var target = $(this).attr("href");
        if (target.length > 1 && target.charAt(0) == "#") {
            highlightQuestion(target);
        }
    });

    // Make the side navigation dock to the top of the window when the user
    // scrolls past its starting position (but stop at the last question).
    var $navigation = $("#content-secondary .navigation");
    var top = $navigation.offset().top;

    // Calculate where the side navigation should stop scrolling.
    var $lastQuestion = $("ol.questions > li:last-child");
    var bottom = $lastQuestion.offset().top + $lastQuestion.outerHeight()
            - $navigation.outerHeight();

    console.log(top, bottom, $lastQuestion.text());

    $(document).scroll(function() {
        var scrollTop = $(this).scrollTop();
        if (scrollTop >= bottom) {
            $navigation.css({
                position: "absolute",
                top: bottom
            });
        } else if (scrollTop >= top) {
            $navigation.css({
                position: "fixed",
                top: 0
            });
        } else {
            $navigation.css("position", "static");
        }
    });

    // Highlight the question referenced in the URL.
    highlightQuestion(window.location.hash);
});
