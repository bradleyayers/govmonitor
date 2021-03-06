/**
 * The create/edit reference form.
 */
AP.ReferenceFormView = Backbone.View.extend({
  events: {
    "input #id_title": "_titleChanged",
    "input #id_url": "_fetchTitle",
    "focus .fields input": AP.showInputHelp,
    "focus select": AP.showInputHelp,
    "focus textarea": AP.showInputHelp
  },

  initialize: function() {
    _.bindAll(this);
    this.$("#id_stance").focus();
    AP.showInputHelp();
  },

  /**
   * Pre-fill the title by fetching the title of the document at the given URL.
   */
  _fetchTitle: function() {
    clearTimeout(this._fetchTitleTimeout);
    if (this._titleLocked === true) {
      return;
    }

    var $title = this.$("#id_title");
    var $url = this.$("#id_url");
    if ($url.val() === "") {
      $title.val("");
      return;
    }

    var instance = this;
    this._fetchTitleTimeout = setTimeout(function() {
      var request = $.ajax("/ajax/title/?url=" + $url.val());

      request.done(function(data) {
        $title.val(data);
      });

      request.fail(function() {
        $title.val("");
      });

      request.always(function() {
        $title.removeAttr("disabled");
        $title.removeClass("loading");
      });

      $title.addClass("loading");
      $title.attr("disabled", "disabled");
    }, 200);
  },

  /**
   * Locks or unlocks the title field in reponse to user input.
   *
   * If the title field is locked, we don't attempt to autofill it.
   */
  _titleChanged: function() {
    this._titleLocked = this.$("#id_title").val() !== "";
  }
});
