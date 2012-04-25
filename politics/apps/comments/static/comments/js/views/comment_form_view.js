AP.namespace("AP.Comments");

/**
 * A comment creation/editing form.
 */
AP.Comments.FormView = Backbone.View.extend({
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

    model: AP.Comments.Comment,

    initialize: function() {
        _.bindAll(this);
        this.render();
    },

    /**
     * Triggers the cancel event if it's OK to discard the user's changes.
     *
     * Called when the cancel button is clicked.
     *
     * @private
     */
    _cancelClicked: function(e) {
        if (e) {
            e.preventDefault();
        }

        if (!this.$el.hasClass("loading")) {
            var message = "You will lose your comment if you continue.";
            if (!this._isDirty() || confirm(message)) {
                this.trigger("cancel");
            } else {
                this.$("textarea").focus();
            }
        }
    },

    /**
     * Triggers the submit event if the comment model is valid.
     *
     * Called when the form is submitted.
     *
     * @private
     */
    _formSubmitted: function(e) {
        e.preventDefault();

        this._updateModel();
        if (this._validate()) {
            this.trigger("submit");
        } else {
            this.$("textarea").focus();
        }
    },

    /**
     * Determine if the form has unsaved changes.
     *
     * @private
     * @returns {boolean} true iff the form has unsaved changes.
     */
    _isDirty: function() {
        this._updateModel();
        return this.model.get("body").length > 0;
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
     * Remove the form.
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
          "<textarea name='body'></textarea>",
          "<div>",
            "<input type='submit' value='Add'/>",
            "<a class='cancel' href='#'>Cancel</a>",
          "</div>",
        ].join(""));

        this.$el.html(template());
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
     * @private
     * @param {string} message The error message to show.
     */
    showErrorMessage: function(message) {
        this.$(".error").remove();
        this.$("textarea").after($("<p class='error'/>").text(message));
    },

    /**
     * Update the comment model to reflect the current state of the form.
     *
     * @private
     */
    _updateModel: function() {
        this.model.set({
            body: this.$("textarea").val()
        });
    },

    /**
     * Validates the comment model, showing error messages as needed.
     *
     * @private
     * @returns {boolean} true iff the comment model is in a valid state.
     */
    _validate: function() {
        if (!this.model.get("body").length) {
            this.showErrorMessage("Your comment can't be empty!");
            return false;
        }

        return true;
    }
});
