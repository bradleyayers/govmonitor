(function() {
    /**
     * Behaves the same as Backbone.Event's on method, but invokes the callback
     * at most once (unbinds it automatically). Useful for memory management.
     */
    Backbone.Events.one = function(events, callback, context) {
        var instance = this;
        var unbindingCallback = function() {
            instance.off(events, unbindingCallback, context);
            callback.apply(context, arguments);
        };

        this.on(events, unbindingCallback, context);
    };
})();
