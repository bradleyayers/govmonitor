AP.RequestFormView = Backbone.View.extend({
    events: {
        "submit": "_onSubmit"
    },

    initialize: function() {
        _.bindAll(this);
    },

    _onSubmit: function(e) {
        e.preventDefault();

        var $contact = this.$("input[name=contact]");
        if ($contact.val() === "") {
            $contact.focus();
            return;
        }

        // Disable the inputs while waiting for AJAX.
        var $submit = this.$("input[type=submit]");
        $contact.attr("disabled", "disabled");
        $submit.attr("disabled", "disabled");

        var request = $.ajax({
            data: {
                contact: $contact.val(),
                query: this.$("input[name=query]").val()
            },
            type: "POST",
            url: "/request/"
        });

        request.done(_.bind(function() {
            this.$("div.inputs").remove();
            this.$("p.success").css({
                display: "inline"
            });
        }, this));

        request.fail(function() {
            alert("Oops, something broke. Try again!");
            $contact.removeAttr("disabled");
            $submit.removeAttr("disabled");
        });
    }
});