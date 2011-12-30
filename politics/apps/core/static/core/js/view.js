com.chrisdoble.addInitialiser(function() {
    $("div.reference div.vote-widget a").click(function() {
        var link = $(this);
        var path = "/references/" + link.siblings("input").val() + "/votes/";

        if (link.hasClass("selected")) {
            // Deselect before we make the request to make things seem faster.
            link.attr("title", "Select this reference.");
            link.removeClass("selected");

            $.ajax(path, {
                "type": "DELETE",
                "error": function() {
                    link.addClass("selected");
                    link.attr("title", "Deselect this reference.");
                }
            });
        } else {
            var previousLink = $("div.reference div.vote-widget a.selected");

            // Again, change the selections before making the request to make
            // things seem faster. We'll re-select these if anything fails.
            link.addClass("selected");
            link.attr("title", "Deselect this reference.");
            previousLink.removeClass("selected");

            $.ajax(path, {
                "type": "POST",
                "error": function(response) {
                    if (response.status == 401) {
                        alert("Log in to vote.");
                    } else {
                        alert("Oops, something went wrong.");
                    }

                    link.attr("title", "Select this reference.");
                    link.removeClass("selected");
                    previousLink.addClass("selected");
                }
            });
        }
    });
});
