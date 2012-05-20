/**
 * A list of suggestions, attached to a text input.
 *
 * Users can highlight and select suggestions using the keyboard or mouse.
 *
 * To be notified on selection of a suggestion, users of this view should bind
 * to the "select" event. The selected suggestion object will be passed.
 */
AP.SuggestionList = Backbone.View.extend({
  tagName: "ol",
  className: "suggestions",

  /**
   * Initialise and display the view.
   *
   * @param {element} input The input to attach to
   * @param {Array<String>} suggestions The suggestions to show.
   */
  initialize: function(input, suggestions) {
    _.bindAll(this);
    this.$input = $(input);
    this.suggestions = suggestions;

    this.render();
    this._attachToInput();
  },

  /**
   * Attach the view to an input and display it.
   *
   * Attaching to an input involves positioning the view below said input and
   * binding to its key events so we know when to highlight different options.
   *
   * @param {element} input The element to attach to.
   */
  _attachToInput: function() {
    this.$el.css({
      left: this.$input.offset().left,
      top: this.$input.offset().top + this.$input.outerHeight(),
      width: this.$input.outerWidth()
    });

    $("body").append(this.$el);
    $("body").bind("click", this._clickBody);
    this.$input.on("keydown", this._keyDown);
  },

  /**
   * Dismiss the suggestions list if the user clicked off the input.
   */
  _clickBody: function(e) {
    var $target = $(e.target);
    var inInput = $target.closest(this.$input).length;
    var inList = $target.closest(this.$el).length;

    if (!(inInput || inList)) {
      this.remove();
    }
  },

  /**
   * Selects the item that was clicked.
   */
  _clickItem: function(e) {
    this._select($(e.target).closest("li").index());
  },
  
  /**
   * Returns the index of the currently highlighted item.
   *
   * Returns -1 if no item is currently selected.
   */
  _getHighlightedIndex: function() {
    return this.$(".highlighted").index();
  },

  /**
   * Highlight the item at a particular index.
   *
   * @param {number} i The index of the item to highlight.
   */
  _highlight: function(i) {
    this.$("li").removeClass("highlighted");
    this.$("li").eq(i).addClass("highlighted");
  },

  /**
   * Highlight the next item in the list.
   *
   * If no item is currently highlighted, highlight the first item in the list.
   */
  _highlightNext: function() {
    if (this._getHighlightedIndex() == -1) {
      this._highlight(0);
    } else {
      var i = (this._getHighlightedIndex() + 1) % this.suggestions.length;
      this._highlight(i);
    }
  },

  /**
   * Highlight the previous item in the list.
   *
   * If no item is currently highlighted, highlight the last item in the list.
   */
  _highlightPrevious: function() {
    if (this._getHighlightedIndex() == -1) {
      this._highlight(this.suggestions.length - 1);
    } else {
      var i = this._getHighlightedIndex() - 1;
      i = i < 0 ? this.suggestions.length - 1 : i;
      this._highlight(i);
    }
  },

  /**
   * Returns true iff the suggestion list is visible.
   */
  isVisible: function() {
    return !!this.$el.closest("html").length;
  },

  /**
   * Select an item, close the list, or move the highlight.
   */
  _keyDown: function(e) {
    if (e.keyCode == 13) {
      var i = this._getHighlightedIndex();
      if (i !== -1) {
        e.preventDefault();
        this._select(i);
      }
    } else if (e.keyCode == 27) {
      this.remove();
    } else if (e.keyCode == 38) {
      this._highlightPrevious();
    } else if (e.keyCode == 40) {
      this._highlightNext();
    }
  },

  /**
   * Highlight an item when the user mouses over it.
   */
  _mouseOver: function(e) {
    this._highlight($(e.target).closest("li").index());
  },

  /**
   * Hide and remove the view, allowing it to be GCed.
   */
  remove: function() {
    this.$el.remove();
    this.$input.off("keydown", this._keyDown);
    $("body").off("click", this._clickBody);
  },

  /**
   * Render the suggestions list.
   */
  render: function() {
    var template = _.template([
      "<% for (var i in suggestions) { %>",
        "<li><%- suggestions[i] %></li>",
      "<% } %>"
    ].join(""));

    this.$el.html(template({suggestions: this.suggestions}));
    this.$("li").on({
      click: this._clickItem,
      mouseover: this._mouseOver
    });
  },

  /**
   * Select the suggestion at a particular index.
   *
   * Triggers a "select" event that the creator of the suggestion list can bind
   * to. The selected suggestion object is passed as an argument to the event.
   *
   * @param {number} i The index of the suggestion that is to be selected.
   */
  _select: function(i) {
    this.trigger("select", this.suggestions[i]);
  }
});
