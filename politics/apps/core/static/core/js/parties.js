$(function() {
  $("form.party").each(function() {
    new AP.PartyFormView({
      el: this
    });
  });
});