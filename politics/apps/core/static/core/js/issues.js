com.chrisdoble.addInitialiser(function() {
    var tagsInput = $("form.issue #tags");

    // The list of tag suggestions.
    function SuggestionsBox(suggestions) {
        var list = $("<ol class=\"tag_suggestions\"/>");
        for (var i = 0; i < 5 && i < suggestions.length; i++) {
            var item = $("<li>" + suggestions[i] + "</li>").appendTo(list);

            item.click(function(tag) {
                return function() {
                    var tags = tagsInput.val().split(" ");
                    tagsInput.val(tags.slice(0, -1).concat(tag).join(" "));
                    tagsInput.focus();
                };
            }(suggestions[i]));

            item.hover(function(e) {
                list.children().removeClass("hover");
                if (e.type == "mouseenter") {
                    $(this).addClass("hover");
                }
            });
        }

        // Minus 1 so their borders overlap.
        list.css("top", tagsInput.offset().top + tagsInput.outerHeight() - 1);
        list.css("left", tagsInput.offset().left);
        tagsInput.after(list);
        tagsInput.data("suggestionsBox", this);

        this.currentItem = function() {
            return $("li.hover", list).first();
        };

        this.remove = function() {
            list.remove();
            tagsInput.data("suggestionsBox", undefined);
        };

        this.selectNextItem = function() {
            var currentItem = this.currentItem();

            if (!currentItem.length) {
                list.children().first().addClass("hover");
            } else if (currentItem.next().length) {
                currentItem.removeClass("hover");
                currentItem.next().addClass("hover");
            }
        };

        this.selectPreviousItem = function() {
            var currentItem = this.currentItem();

            if (!currentItem.length) {
                list.children().last().addClass("hover");
            } else if (currentItem.prev().length) {
                currentItem.removeClass("hover");
                currentItem.prev().addClass("hover");
            }
        };
    }

    function requestSuggestions() {
        $.ajax({
            "url": "/ajax/tags/?q=" + tagsInput.val().split(" ").pop(),
            "success": function(data) {
                var suggestionsBox = tagsInput.data("suggestionsBox");
                if (suggestionsBox) {
                    suggestionsBox.remove();
                }

                SuggestionsBox(data);
            }
        });
    }

    $(document).click(function() {
        var suggestionsBox = tagsInput.data("suggestionsBox");
        if (suggestionsBox) {
            suggestionsBox.remove();
        }
    });

    tagsInput.keydown(function(e) {
        var suggestionsBox = tagsInput.data("suggestionsBox");

        // Enter.
        if (e.keyCode == 13) {
            var item = suggestionsBox ? suggestionsBox.currentItem() : null;
            if (item) {
                item.click();
                e.preventDefault();
                suggestionsBox.remove();
            }
        // Up arrow.
        } else if (e.keyCode == 38) {
            if (suggestionsBox) {
                e.preventDefault();
                suggestionsBox.selectPreviousItem();
            }
        // Down arrow.
        } else if (e.keyCode == 40) {
            if (suggestionsBox) {
                suggestionsBox.selectNextItem();
            }
        }
    });

    tagsInput.keyup(function(e) {
        var suggestionsBox = tagsInput.data("suggestionsBox");

        if ($.inArray(e.keyCode, [13, 16, 17, 18, 38, 40, 91, 93, 224]) != -1) {
            return;
        } else {
            clearTimeout(tagsInput.data("timeoutID"));

            if (tagsInput.val() == "" || tagsInput.val().slice(-1) == " ") {
                if (suggestionsBox) {
                    suggestionsBox.remove();
                }
            } else {
                tagsInput.data("timeoutID", setTimeout(requestSuggestions, 500));
            }
        }
    });

    $("form.issue #name").focus();
});