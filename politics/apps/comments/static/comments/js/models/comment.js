AP.namespace("AP.Comments");

/**
 * A comment.
 */
AP.Comments.Comment = Backbone.Model.extend({
    defaults: {
        "body": "",
        "is_editable": true,
        "is_own": true
    },

    /**
     * Destroy the comment on the server.
     *
     * @param {object} options
     * @param {function} options.error A function to be executed on error.
     */
    destroy: function(options) {
        var instance = this;
        var success = function(data) {
            instance.set(_.extend(data, {is_editable: false}));
        };

        $.ajax({
            dataType: "json",
            error: options.error,
            success: success,
            type: "DELETE",
            url: this.url()
        });
    },

    /**
     * Returns the relative URL to the comment resource on the server.
     *
     * @returns {string} The relative URL to the comment resource on the server.
     */
    url: function() {
        return "/comments/" + this.get("id") + "/";
    },

    /**
     * Save the comment to the server.
     *
     * Assumes that the comment already exists.
     *
     * @param {object} options
     * @param {function} options.success A function to be executed on success.
     */
    save: function(options) {
        var instance = this;
        var success = function(data) {
            (options.success || $.noop)(instance.set(data));
        };

        $.ajax({
            data: "body=" + this.get("body"),
            dataType: "json",
            error: options.error,
            success: success,
            type: "PUT",
            url: this.url()
        });
    },

    /**
     * Validates the given attributes.
     *
     * @param {object} attributes The attributes to be validated.
     * @returns undefined if valid, an error message if invalid.
     */
    validate: function(attributes) {
        if (!attributes.body || attributes.body.length === 0) {
            return "A comment can't be empty!";
        }
    }
});
