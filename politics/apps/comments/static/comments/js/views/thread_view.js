AP.namespace("AP.Comments");

/**
 * A thread of comments.
 */
AP.Comments.ThreadView = Backbone.View.extend({
    events: {
        "click .add-comment": "addCommentClicked"
    },

    initialize: function() {
        _.bindAll(this);
        this.collection.bind("add", this._createCommentView);
    },

    /**
     * Hides the add comment link and shows a "new comment" form.
     */
    addCommentClicked: function(e) {
        e.preventDefault();

        var instance = this;
        var addComment = this.$(".add-comment");
        var form = new AP.Comments.FormView({
            model: new AP.Comments.Comment()
        });

        form.on("cancel", function() {
            addComment.show();
            form.remove();
        });

        form.on("submit", function() {
            var success = function(comment) {
                instance.collection.add(comment);
                addComment.show();
                form.remove();
            };

            var error = function() {
                form.setLoading(false);
                form.showErrorMessage("Something broke and your comment couldn't be added.");
            };

            form.setLoading(true);
            instance.collection.createComment(form.model, success, error);
        });

        addComment.hide();
        this.$el.append(form.el);
        form.$("textarea").focus();
    },

    /**
     * Creates a view for a comment and appends it to the thread.
     *
     * @private
     * @param {AP.Comments.Comment} comment The comment.
     */
    _createCommentView: function(comment) {
        var commentView = new AP.Comments.CommentView({
            model: comment
        }).render();

        this.$("ol").append(commentView.el);
    }
}, {
    /**
     * Construct the view and its collection from an existing element.
     *
     * @param {element} el The element from which the view is to be created.
     * @returns {AP.Comments.ThreadView} The resulting view.
     */
    fromElement: function(el) {
        var path = $(el).closest("[data-comment-path]").data("comment-path");
        var comments = $(".comment", el).map(function(commentEl) {
            var commentView = AP.Comments.CommentView.fromElement(commentEl);
            return commentView.model;
        });

        return new AP.Comments.ThreadView({
            collection: new AP.Comments.Thread(comments, {path: path}),
            el: el
        });
    }
});
