AP.namespace("AP.Comments");

/**
 * A comment.
 */
AP.Comments.CommentView = Backbone.View.extend({
    model: AP.Comments.Comment,

    tagName: "li",
    className: "comment",

    events: {
        "click .delete": "_deleteClicked",
        "click .edit": "_editClicked"
    },

    initialize: function() {
        _.bindAll(this);
        this.model.on("change", this.render);
    },

    /**
     * Attempts to delete the comment.
     */
    _deleteClicked: function(e) {
        e.preventDefault();

        // Fires a change event, causing a render.
        if (confirm("Delete this comment?")) {
            this.model.destroy({
                error: function() {
                    alert("Something broke and your comment couldn't be deleted.");
                }
            });
        }
    },

    /**
     * Transitions the comment into editing mode.
     */
    _editClicked: function(e) {
        e.preventDefault();

        // Don't destroy our contents as we may not have enough information to
        // re-render it; just detach it so we can restore it later if necessary.
        var contents = this.$el.contents().detach();
        var form = new AP.Comments.FormView({
            model: this.model
        });

        var instance = this;
        form.on("cancel", function() {
            form.remove();
            instance.$el.empty();
            instance.$el.append(contents);
        });

        form.on("submit", function() {
            var error = function() {
                form.setLoading(false);
                alert("Something broke and your changes couldn't be saved.");
            };

            var success = function(comment) {
                form.remove();
                instance.model = comment;
                instance.render();
            };

            form.setLoading(true);
            form.buildModel().save({
                error: error,
                success: success
            });
        });

        this.$el.append(form.$el);
        form.$("textarea").focus().select();
    },

    /**
     * Render the view.
     */
    render: function() {
        var template = _.template([
            "<% if (is_deleted) { %>",
              "<div class='body' title='Deleted'>Deleted</div>",
            "<% } else { %>",
              "<div class='body'><%- body %></div>",
            "<% } %>",
            " — <a href='/users/<%- author.id %>/'>",
                "<%- author.first_name %> <%- author.last_name %>",
            "</a>",
            "<% if (is_editable && !is_deleted) { %>",
                " <a class='edit icon-pencil' href='#'>Edit</a>",
                " <a class='delete' href='#' title='Delete'></a>",
            "<% } %>",
        ].join(""));

        this.$el.removeClass();
        this.$el.addClass("comment");
        this.$el.attr("id", "comment-" + this.model.get("id"));
        this.$el.html(template(this.model.toJSON()));

        if (this.model.get("is_deleted")) {
            this.$el.addClass("deleted");
        }

        if (this.model.get("is_own")) {
            this.$el.addClass("own");
        }

        return this;
    }
}, {
    /**
     * Construct the view and its model from an existing element.
     *
     * @param {element} el The element from which the view is to be created.
     * @returns {AP.Comments.CommentView} The resulting view.
     */
    fromElement: function(el) {
        var $el = $(el);
        var comment = new AP.Comments.Comment({
            body: $(".body", el).text(),
            id: $el.data("id"),
            is_own: $el.has(".delete").length
        });

        return new AP.Comments.CommentView({
            el: el,
            model: comment
        });
    }
});
