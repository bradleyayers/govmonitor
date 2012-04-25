AP.namespace("AP.Comments");

/**
 * A comment.
 */
AP.Comments.CommentView = Backbone.View.extend({
    model: AP.Comments.Comment,

    tagName: "li",
    className: "comment",

    /**
     * Render the view.
     */
    render: function() {
        var template = _.template([
          "<%- body %> — ",
          "<a href='/users/<%- author.id %>/'>",
              "<%- author.first_name %> <%- author.last_name %>",
          "</a>"
        ].join(""));

        this.$el.attr("id", "comment-" + this.model.get("id"));
        this.$el.html(template(this.model.toJSON()));
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
        return new AP.Comments.CommentView({
            el: el,
            model: new AP.Comments.Comment()
        });
    }
});
