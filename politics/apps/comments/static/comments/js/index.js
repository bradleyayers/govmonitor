$(function() {
    $(".commentable").each(function() {
        AP.Comments.CommentableView.fromElement(this);
    });

    // Highlight the target comment.
    var hash = window.location.hash;
    if (hash !== "") {
        $(".comment-thread " + hash).addClass("highlighted");
    }
});
