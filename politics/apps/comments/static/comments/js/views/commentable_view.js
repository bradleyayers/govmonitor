AP.namespace("AP.Comments");

/**
 * An object that may be commented on.
 */
AP.Comments.CommentableView = Backbone.View.extend({
  events: {
    "click .add-comment": "_addCommentClicked"
  },

  initialize: function(options) {
      _.bindAll(this);
      this.threadView = options.threadView;
  },

  /**
   * Shows the comment form in the thread view.
   *
   * @private
   */
  _addCommentClicked: function(e) {
    e.preventDefault();

    if (AP.meta("logged-in")) {
      this.threadView.showCommentForm();
    } else {
      e.stopPropagation();
      AP.showLogInTooltip(e.target, {verb: "comment"});
    }
  },

  _createLogInTooltip: function(el) {
    $(el).tooltip({
    });
  }
}, {
  /**
   * Construct the view from an existing element.
   *
   * Instances should always be created using this method. Assumes that `el`
   * has one comment thread descendant (an element with class comment-thread).
   *
   * @param {element} el The element form which the view is to be created.
   * @returns {AP.Comments.CommentableView} The resulting view.
   */
  fromElement: function(el) {
    var threadEl = $(".comment-thread", el).get(0);
    var threadView = AP.Comments.ThreadView.fromElement(threadEl);

    return new AP.Comments.CommentableView({
      el: el,
      threadView: threadView
    });
  }
});
