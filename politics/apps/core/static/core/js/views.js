$(function() {
  $("div.reference").each(function() {
    new AP.ReferenceView({
      el: this
    });
  });

  $("html.search form.request").each(function() {
    new AP.RequestFormView({
      el: this
    });
  });
});