AP.namespace("AP.Comments");

/**
 * A comment creation/editing form.
 */
AP.Comments.FormView = Backbone.View.extend({
    model: AP.Comments.Comment,

    tagName: "form",
    className: "comment-form",
    attributes: {
        action: "",
        method: "POST"
    },

    events: {
        "click .cancel": "_cancelClicked",
        "keyup": "_keyPressed",
        "submit": "_formSubmitted"
    },

    initialize: function() {
        _.bindAll(this);
        this.render();
    },

    /**
     * Builds and returns a comment from the form's state.
     *
     * @returns {AP.Comments.Comment} A comment built from the form's state.
     */
    buildModel: function() {
        return this.model.clone().set({
            body: this._getBody()
        });
    },

    /**
     * Triggers the cancel event if it's OK to discard the user's changes.
     *
     * Called when the cancel button is clicked.
     *
     * @private
     */
    _cancelClicked: function(e) {
        // Because this is called from _keyPressed.
        if (e) {
            e.preventDefault();
        }

        if (!this.$el.hasClass("loading")) {
            var message = "You will lose your changes if you continue.";
            if (!this._isDirty() || confirm(message)) {
                this.trigger("cancel");
            } else {
                this.$("textarea").focus();
            }
        }
    },

    /**
     * Triggers the submit event if the form's content is valid.
     *
     * Called when the form is submitted.
     *
     * @private
     */
    _formSubmitted: function(e) {
        e.preventDefault();

        var attributes = {body: this._getBody()};
        var errorMessage = this.model.validate(attributes);

        if (errorMessage) {
            this.showErrorMessage(errorMessage);
            this.$("textarea").focus();
        } else {
            this.trigger("submit");
        }
    },

    /**
     * Returns the form's body value.
     *
     * @private
     * @returns {string} The form's body value.
     */
    _getBody: function() {
        return this.$("textarea").val();
    },

    /**
     * Determine if the form has unsaved changes.
     *
     * @private
     * @returns {boolean} true iff the form has unsaved changes.
     */
    _isDirty: function() {
        return this._getBody() !== this.model.get("body");
    },

    /**
     * Cancels the form if escape was pressed.
     *
     * Called when a key is pressed.
     *
     * @private
     */
    _keyPressed: function(e) {
        if (e.keyCode == 27) {
            this._cancelClicked();
        }
    },

    /**
     * Remove the form and unbind all event handlers.
     */
    remove: function() {
        this.$el.remove();
        this.off();
    },

    /**
     * Render the form.
     */
    render: function() {
        var template = _.template([
          "<textarea name='body'><%- body %></textarea>",
          "<div>",
            "<input type='submit' value='<%- submitLabel %>'/>",
            "<a class='cancel' href='#'>Cancel</a>",
          "</div>",
        ].join(""));

        var data = _.extend(this.model.toJSON(), {
            submitLabel: this.model.id ? "Save" : "Add"
        });

        this.$el.html(template(data));
        return this;
    },

    /**
     * Set whether the form is in the loading state.
     *
     * When in the loading state, interaction with the form's controls is
     * disabled and an indeterminate progress indicator (spinner) is shown.
     *
     * @param {boolean} loading Whether the form should be in the loading state.
     */
    setLoading: function(loading) {
        if (loading) {
            this.$el.addClass("loading");
            this.$(":submit").attr("disabled", "");
            this.$("textarea").attr("disabled", "");
        } else {
            this.$el.removeClass("loading");
            this.$(":submit").removeAttr("disabled");
            this.$("textarea").removeAttr("disabled");
        }
    },

    /**
     * Show an error message in the form.
     *
     * @param {string} message The error message to show.
     */
    showErrorMessage: function(message) {
        this.$(".error").remove();
        this.$("textarea").after($("<p class='error'/>").text(message));
    }
});
