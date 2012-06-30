/**
 * A reference that can be voted on.
 */
AP.ReferenceView = Backbone.View.extend({
  events: {
    "click .score div a": "_vote",
  },

  // Assumes $el is set.
  initialize: function() {
    _.bindAll(this);

    // If the user has voted on this reference, select the appropriate button.
    var pk = this.$el.data("pk");
    if (AP.Votes.isUpvoted(pk)) {
      this.$("[data-vote-type=up]").addClass("selected");
    } else if (AP.Votes.isDownvoted(pk)) {
      this.$("[data-vote-type=down]").addClass("selected");
    }

    // Create the validity help text tooltip. Its title should update
    // automatically to reflect the reference's current score on the page.
    this.$(".score .icon-question-sign").tooltip({
      title: _.bind(function() {
        return this.$(".score > span").text() + " of users think this " +
            "reference accurately reflects the party's views.";
      }, this)
    });
  },

  _getScoreText: function(score) {
    return (score * 100).toFixed(0) + "%";
  },

  // Cast or revoke a vote using information from the event's target (a vote
  // link). Ignores the click if we're waiting for a response to come back.
  _vote: function(e) {
    e.preventDefault();

    if (!AP.meta("logged-in")) {
      AP.showLogInTooltip(this.$("div.score div"), {verb: "vote"});
      e.stopPropagation();
      return;
    }

    // Are we already waiting on a request?
    var $scoreWidget = this.$(".score");
    if ($scoreWidget.hasClass("loading")) {
      return;
    }

    var $a = $(e.target);
    var isDelete = $a.hasClass("selected");
    var request = $.ajax($scoreWidget.data("votes-url"), {
      data: {"type": $a.data("vote-type")},
      type: isDelete ? "DELETE" : "POST"
    });

    var $scoreSpan = $scoreWidget.find("span");
    request.done(_.bind(function(data) {
      $scoreSpan.text(this._getScoreText(data.score));
    }, this));

    // Restore old state on failure.
    var oldHtml = $scoreWidget.html();
    request.fail(function() {
      $scoreWidget.html(oldHtml);
    });

    request.always(function() {
      $scoreWidget.removeClass("loading");
    });

    // Optimistically say we're done.
    $scoreWidget.addClass("loading");
    $scoreWidget.find("a").removeClass("selected");

    if (!isDelete) {
      $a.addClass("selected");
    }
  }
});
