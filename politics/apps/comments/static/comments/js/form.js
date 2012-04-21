AP.namespace("AP.Comments");

/**
 * A comment creation/editing form.
 *
 * Comment forms temporarily replace another element on the page. For a creation
 * form, this will be the "add comment" link; for an edit form, this will be the
 * existing comment. If the "cancel" link is clicked, the element is restored.
 *
 * @param element The element that is to be replaced temporarily.
 */
AP.Comments.Form = function(element) {
    _.extend(this, Backbone.Events);

    var template = _.template([
      "<form action='' method='POST'>",
        "<textarea name='body'></textarea>",
        "<div>",
          "<input type='submit' value='Add'/>",
          "<a class='cancel' href='#'>Cancel</a>",
        "</div>",
      "</form>"
    ].join(""));

    var $form = $(template());
    var $original = $(element);

    /**
     * Returns the form's body value: the user's input.
     *
     * @private
     * @returns {string} The form's current body value.
     */
    var getBody = function() {
        return $("textarea[name='body']", $form).val();
    };

    /**
     * Cancel creating/editing providing the form isn't disabled.
     *
     * The form will be removed and the original element replaced. If the user
     * has made changes to the form, they are asked to confirm cancellation.
     */
    this.cancel = function() {
        if ($form.hasClass("disabled")) {
            return;
        }

        var message = "You will lose your comment if you continue.";
        if (getBody().length === 0 || confirm(message)) {
            this.remove();
        }
    };

    /**
     * Disable the form's elements, preventing interaction.
     */
    this.disable = function() {
        $form.addClass("disabled");
        $(":submit", $form).attr("disabled", "");
        $("textarea", $form).attr("disabled", "");
    };

    /**
     * Enable the form's elements, allowing interaction.
     */
    this.enable = function() {
        $form.removeClass("disabled");
        $(":submit", $form).removeAttr("disabled");
        $("textarea", $form).removeAttr("disabled").focus();
    };

    /**
     * Validate the user's input.
     *
     * @private
     * @returns {boolean} true iff the user's input is valid.
     */
    var isValid = function() {
        return getBody().length > 0;
    };

    /**
     * Remove the form (and restore the original element) without confirmation.
     */
    this.remove = function() {
        $form.replaceWith($original);
        this.off();
    };

    /**
     * Show an error message in the form.
     *
     * @param {string} message The error message to display.
     */
    this.showErrorMessage = function(message) {
        $("p.error", $form).remove();
        $("textarea", $form).after("<p class='error'>" + message + "</p>");
    };

    /**
     * Submit the form if the user's input is valid, otherwise show an error.
     */
    this.submit = function() {
        if (isValid()) {
            this.disable();
            this.trigger("submit", getBody());
        } else {
            this.showErrorMessage("Your comment can't be empty!");
            $("textarea", $form).focus();
        }
    };

    // Hook up the event handlers.
    $form.on({
      "keyup": _.bind(function(e) {
          e.preventDefault();
          if (e.keyCode == 27) {
              this.cancel();
          }
      }, this),
      "submit": _.bind(function(e) {
          e.preventDefault();
          this.submit();
      }, this)
    });

    $("a.cancel", $form).click(_.bind(function(e) {
        e.preventDefault();
        this.cancel();
    }, this));

    // Replace the element and focus the text area.
    $original.after($form);
    $original.detach();
    $("textarea", $form).focus();
};
