AP.Votes = (function() {
  function _isVoted(pk, type) {
    var data = AP.Votes.VoteData;
    return typeof data !== "undefined" && data[pk] === type;
  }

  return {
    /**
     * Returns true iff the current user has an active downvote on the object
     * described by the given primary key. Assumes AP.Votes.VoteData is set.
     */
    isDownvoted: function(pk) {
      return _isVoted(pk, "down");
    },

    /**
     * Returns true iff the current user has an active upvote on the object
     * described by the given primary key. Assumes AP.Votes.VoteData is set.
     */
    isUpvoted: function(pk) {
      return _isVoted(pk, "up");
    }
  };
})();
