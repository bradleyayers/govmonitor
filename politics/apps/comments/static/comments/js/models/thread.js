AP.namespace("AP.Comments");

/**
 * A thread of comments.
 */
AP.Comments.Thread = Backbone.Collection.extend({
    model: AP.Comments.Comment,

    initialize: function(models, options) {
        this.path = options.path;
    },

    /**
     * Attempts to create a new comment on the server.
     *
     * @param {AP.Comments.Comment} comment The comment that is to be created.
     * @param {function} success Executed on success; passed the new comment.
     * @param {function} error Executed on error.
     */
    createComment: function(comment, success, error) {
        success = _.wrap(success, function(f, data) {
            f(new AP.Comments.Comment(data));
        });

        $.ajax({
            data: "body=" + comment.get("body"),
            dataType: "json",
            error: error,
            success: success,
            type: "POST",
            url: this.path
        });
    }
});
