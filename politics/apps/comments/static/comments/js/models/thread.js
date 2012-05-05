AP.namespace("AP.Comments");

/**
 * A thread of comments.
 */
AP.Comments.Thread = Backbone.Collection.extend({
    model: AP.Comments.Comment,

    initialize: function(models, options) {
        _.bindAll(this);
        this.url = options.url;
    },

    /**
     * Attempts to create a new comment on the server.
     *
     * @param {AP.Comments.Comment} comment The comment that is to be created.
     * @param {object} options
     * @param {function} options.error Executed on error.
     * @param {function} options.success Executed on success, takes a single
     *                                   argument: the newly created comment.
     */
    createComment: function(comment, options) {
        var success = function(data) {
            (options.success || $.noop)(new AP.Comments.Comment(data));
        };

        $.ajax({
            data: "body=" + comment.get("body"),
            dataType: "json",
            error: options.error,
            success: success,
            type: "POST",
            url: this.url
        });
    }
});
