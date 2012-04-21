AP.namespace("AP.Comments");

/**
 * An individual comment in a thread.
 *
 * @param element The comment's element.
 */
AP.Comments.Comment = function(element) {
};

/**
 * Creates a new comment from a data object and appends it to a thread element.
 *
 * @param {object} data The data describing the comment that is to be created.
 * @param {element} thread The thread element the comment is to be appended to.
 * @returns {AP.Comments.Comment} The newly created comment object.
 */
AP.Comments.Comment.fromData = function(data, thread) {
    var template = _.template([
      "<li>",
        "<%- body %> — ",
        "<a href='/users/<%- author.id %>/'>",
            "<%- author.first_name %> <%- author.last_name %>",
        "</a>",
      "</li>"
    ].join(""));

    var $element = $(template(data));
    var $comments = $("ol.comments", thread);
    return new AP.Comments.Comment($element.appendTo($comments));
};
