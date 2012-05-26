AP.namespace("AP.Feedback");

/**
 * The feedback form displayed on the side of every page.
 */
AP.Feedback.Form = Backbone.View.extend({
  events: {
    "click a.close": "_close",
    "keydown": "_keydown",
    "mousedown input[type=submit]": "_submit",
    "submit": "_submit"
  },

  /**
   * Initialise the view.
   *
   * @param {object} options
   * @param {element} options.button The button shows the form.
   */
  initialize: function(options) {
    _.bindAll(this);
    this.$textarea = this.$("textarea");

    // We don't need to unbind this (or a "remove" function for that matter)
    // because the feedback form will be present until the user leaves the page.
    $(options.button).on("click", this._show);
  },

  /**
   * Close the form.
   *
   * Asks the user for confirmation if they've typed anything (unless the form
   * is submitting, then it just closes because we don't care about the result).
   */
  _close: function(e) {
    if (e) {
      e.preventDefault();
    }

    var isClean = this.$textarea.val() === "";
    var isFinished = this.$(".success:visible").length > 0;
    var isSubmitting = this.$el.hasClass("submitting");
    var message = "You will lose what you've typed if you cancel.";

    if (isClean || isFinished || isSubmitting || confirm(message)) {
      this.$el.removeClass("submitting");
      this.$el.animate({left: -410}, 400);
      this.$textarea.blur();
    }
  },

  /**
   * Close the form if escape was pressed.
   */
  _keydown: function(e) {
    if (e.keyCode === 27) {
      this._close();
    }
  },

  _removeErrorMessage: function() {
    this.$("p.errors").remove();
  },

  /**
   * Enabled or disable the form's inputs.
   *
   * @param {boolean} enabled Whether the inputs should be enabled.
   */
  _setInputsEnabled: function(enabled) {
    if (enabled) {
      this.$textarea.removeAttr("disabled");
      this.$("input[type=submit]").removeAttr("disabled");
    } else {
      this.$textarea.attr("disabled", "disabled");
      this.$("input[type=submit]").attr("disabled", "disabled");
    }
  },

  /**
   * Show or hide the success message.
   */
  _setSuccessMessageVisible: function(visible) {
    if (visible) {
      this.$("form").hide();
      this.$(".success").show();
    } else {
      this.$("form").show();
      this.$(".success").hide();
    }
  },

  /**
   * Show the form.
   *
   * Resets the form before showing so it's in a "clean" state.
   */
  _show: function(e) {
    e.preventDefault();

    // Reset the form...
    this.$textarea.val("");
    this._removeErrorMessage();
    this._setInputsEnabled(true);
    this._setSuccessMessageVisible(false);

    // ...and animate it in.
    this.$textarea.focus();
    this.$el.animate({left: 0}, 400);
  },

  /**
   * Show an error message.
   *
   * @param {String} message The error message to show.
   */
  _showErrorMessage: function(message) {
    this._removeErrorMessage();
    this.$textarea.after($("<p class='errors'>" + message + "</p>"));
  },

  /**
   * Attempt to submit the feedback.
   */
  _submit: function(e) {
    e.preventDefault();

    var feedback = this.$textarea.val();
    if (feedback !== "") {
      // If the same error message appears again, the user may not realise that
      // it's new. Remove the existing one so there's a "flash" in between them.
      this._removeErrorMessage();
      this._setInputsEnabled(false);
      this.$el.addClass("submitting");

      var request = $.ajax({
        url: "/feedback/",
        type: "POST",
        data: {
          feedback: feedback,
          url: window.location.toString()
        }
      });

      var instance = this;
      request.done(function() {
        // If the form doesn't have the "submitting" class, the user closed it
        // before the response came back and they don't care about the result.
        if (instance.$el.hasClass("submitting")) {
          instance._setSuccessMessageVisible(true);
        }
      });

      request.fail(function() {
        // As above.
        if (instance.$el.hasClass("submitting")) {
          instance._setInputsEnabled(true);
          instance._showErrorMessage("Oops! Something broke.");
        }
      });

      request.always(function() {
        instance.$el.removeClass("submitting");
      });
    } else {
      this._showErrorMessage("You haven't written any feedback!");
    }
  }
})
