(function() {
    /**
     * Behaves the same as Backbone.Event's on method, but invokes the callback
     * at most once (unbinds it automatically). Useful for memory management.
     */
    function one(events, callback, context) {
        var instance = this;
        var unbindingCallback = function() {
            instance.off(events, unbindingCallback, context);
            callback.apply(context, arguments);
        };

        this.on(events, unbindingCallback, context);
    };

    Backbone.Events.one = one;
    Backbone.Model.prototype.one = one;
    Backbone.View.prototype.one = one;
})();
