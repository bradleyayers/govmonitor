/**
 * The create/edit issue form.
 */
AP.IssueFormView = Backbone.View.extend({
  events: {
    "focus .fields input": AP.showInputHelp,
    "focus textarea": AP.showInputHelp,
    "keydown #id_tags": "_tagsKeyDown",
    "keyup #id_tags": "_tagsKeyUp"
  },

  initialize: function() {
    _.bindAll(this);
    this.$("#id_name").focus();
    AP.showInputHelp();
    this.$tagsInput = this.$("#id_tags");
  },

  /**
   * Determines whether the given key code should be ignored by the tags input.
   *
   * This is used to prevent non-modifying keys from firing suggestion requests.
   */
  _isIgnoredKeyCode: function(keyCode) {
    var keyCodes = [9, 13, 16, 17, 18, 27, 35, 36, 37, 38, 39, 40, 91, 93, 224];
    return _.indexOf(keyCodes, keyCode) !== -1;
  },

  /**
   * Make an AJAX request for tag suggestions.
   */
  _requestTagSuggestions: function() {
    $.ajax({
      success: this._showTagSuggestions,
      url: "/ajax/tags/?q=" + this.$tagsInput.val().split(" ").pop()
    });
  },

  _showTagSuggestions: function(data) {
    // Remove the existing suggestion list (if any).
    var $tagsInput = this.$tagsInput;
    var suggestionList = $tagsInput.data("suggestionList");
    if (suggestionList) {
      suggestionList.remove();
      $tagsInput.removeData("suggestionList");
    }

    if (data.length) {
      suggestionList = new AP.SuggestionList($tagsInput, data);
      suggestionList.one("select", function(tag) {
        var tags = $tagsInput.val().split(" ");
        $tagsInput.val(tags.slice(0, -1).concat(tag).join(" "));
        $tagsInput.focus();
        suggestionList.remove();
      });

      $tagsInput.data("suggestionList", suggestionList);
    }
  },

  _tagsKeyDown: function(e) {
    // Pressing down/up moves the cursor to the end/start of the input. If the
    // suggestion list is open, this shouldn't happen as it moves the highlight.
    var suggestionList = this.$tagsInput.data("suggestionList");
    var suggestionListVisible = suggestionList && suggestionList.isVisible();
    if (suggestionListVisible && (e.keyCode == 38 || e.keyCode == 40)) {
      e.preventDefault();
    }
  },

  /**
   * Initiate tag suggestions.
   */
  _tagsKeyUp: function(e) {
    // Ignore keys that don't change the content of the input (e.g. arrow keys).
    // Without this, pressing down, up, etc. would recreate the suggestion list.
    if (this._isIgnoredKeyCode(e.keyCode)) {
      return;
    }

    // Cancel the existing suggestions request (if any).
    var timeoutId = this.$tagsInput.data("suggestionsTimeoutId");
    if (timeoutId) {
      window.clearTimeout(timeoutId);
    }

    if (this.$tagsInput.val() !== "") {
      timeoutId = window.setTimeout(this._requestTagSuggestions, 250);
      this.$tagsInput.data("suggestionsTimeoutId", timeoutId);
    }
  }
});
