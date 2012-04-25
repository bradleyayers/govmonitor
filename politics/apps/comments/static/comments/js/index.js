$(function() {
    $("div.comment-thread").each(function() {
        AP.Comments.ThreadView.fromElement(this);
    });

    // Highlight the target comment.
    var hash = window.location.hash;
    if (hash !== "") {
        $("div.comment-thread " + hash).addClass("highlighted");
    }
});
