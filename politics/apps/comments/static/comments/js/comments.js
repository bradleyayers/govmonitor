$(function() {
    $("div.comment-thread").each(function() {
        new AP.Comments.Thread(this);
    });
});
