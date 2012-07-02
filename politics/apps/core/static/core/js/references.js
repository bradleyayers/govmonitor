$(function() {
  $("form.reference").each(function() {
    new AP.ReferenceFormView({
      el: this
    });
  });
});
