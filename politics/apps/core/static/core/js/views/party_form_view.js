/**
 * The create party form.
 */
AP.PartyFormView = Backbone.View.extend({
    events: {
        "focus .fields input": AP.showInputHelp,
        "focus .fields select": AP.showInputHelp
    },

    initialize: function() {
        this.$("#id_parent").focus();
        AP.showInputHelp();
    }
});