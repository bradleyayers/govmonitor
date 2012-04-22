$(function() {
    $("div.comment-thread").each(function() {
        new AP.Comments.Thread(this);
    });

    // Highlight the target comment.
    var hash = window.location.hash;
    if (hash !== "") {
        $("div.comment-thread " + hash).addClass("highlighted");
    }
});
