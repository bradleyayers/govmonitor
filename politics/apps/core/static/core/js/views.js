$(function() {
  $("div.reference").each(function() {
    new AP.ReferenceView({
      el: this
    });
  });
});