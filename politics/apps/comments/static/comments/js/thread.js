AP.namespace("AP.Comments");

/**
 * A thread of comments (or a subset thereof).
 *
 * @param element The thread's container element.
 */
AP.Comments.Thread = function(element) {
    var form;

    /**
     * Returns the path AJAX requests are to be made to.
     *
     * @private
     * @returns {sting} The path that AJAX requests are to be made to.
     */
    var getCommentPath = function() {
        return $(element).closest("[data-comment-path]").data("comment-path");
    };

    /**
     * Create a new comment.
     *
     * @private
     * @param body The body of the new comment (assumed valid).
     */
    var createComment = function(body) {
        var error = function() {
            form.enable();
            form.showErrorMessage("Something broke and your comment couldn't be created.");
        };

        var success = function(data) {
            form.remove();
            form = undefined;
            AP.Comments.Comment.fromData(data, element);
        };

        $.ajax({
            data: "body=" + body,
            dataType: "json",
            error: error,
            success: success,
            type: "POST",
            url: getCommentPath(),
        });
    };

    // Show a form when the "add comment" link is clicked.
    $("a.add-comment", element).click(function(e) {
        e.preventDefault();
        form = new AP.Comments.Form(this);
        form.one("submit", createComment);
    });
};
