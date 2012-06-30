AP.namespace("AP.Comments");

/**
 * A thread of comments.
 */
AP.Comments.ThreadView = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this);
        this.collection.bind("add", this._createCommentView);
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
    },

    /**
     * Remove the comment form.
     *
     * @private
     */
    _removeForm: function() {
        this.form.$el.parent().remove();
        delete this.form;

        // If there are no comments, remove the chrome.
        if (this.$("ol li").length === 0) {
            this.$el.html("");
        }
    },

    render: function() {
        this.$el.html([
            "<div class='arrow'></div>",
            "<ol></ol>"
        ].join(""));
    },

    /**
     * Shows a comment form at the bottom of the thread.
     */
    showCommentForm: function() {
        // Is there already a form?
        if (this.form) {
            this.form.focus();
            return;
        }

        var form = this.form = new AP.Comments.FormView({
            model: new AP.Comments.Comment()
        });

        var instance = this;
        form.on("cancel", function() {
            instance._removeForm();
        });

        form.on("submit", function() {
            var error = function() {
                form.setLoading(false);
                form.showErrorMessage("Something broke and your comment couldn't be added.");
            };

            var success = function(comment) {
                instance.collection.add(comment);
                instance._removeForm();
            };

            form.setLoading(true);
            instance.collection.createComment(form.buildModel(), {
                error: error,
                success: success
            });
        });

        // Do we need to render? If there were no comments on page load, `el`
        // will be empty and we'll need to render the chrome into it.
        if (this.$("ol").length === 0) {
            this.render();
        }

        var formEl = $("<li></li>").append(form.el);
        this.$("ol").append(formEl);
        form.focus();
    }
}, {
    /**
     * Construct the view and its collection from an existing element.
     *
     * @param {element} el The element from which the view is to be created.
     * @returns {AP.Comments.ThreadView} The resulting view.
     */
    fromElement: function(el) {
        var url = $(el).closest("[data-comments-url]").data("comments-url");
        var comments = $(".comment", el).map(function() {
            return AP.Comments.CommentView.fromElement(this).model;
        });

        return new AP.Comments.ThreadView({
            collection: new AP.Comments.Thread(comments, {url: url}),
            el: el
        });
    }
});
