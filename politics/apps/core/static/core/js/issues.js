$(function() {
  // If there's an issue form, create a view for it. We use the content div
  // instead of the form element iself because the sidebar content changes.
  if ($("form.issue").length) {
    new AP.IssueForm({
      el: $("#content-content")
    });
  }

  if ($("html").hasClass("issue")) {
    // Draw the stance distribution chart. Google charts is initialised in its
    // own script tag on the page. Chart data is in a global variable `stances`.
    google.setOnLoadCallback(function() {
      var data = new google.visualization.DataTable();
      data.addColumn("string", "Stance");
      data.addColumn("number", "Parties");

      $.each(stances, function(i, stance) {
        data.addRow(stance);
      });

      var options = {
        "backgroundColor": "#F9F4F3",
        "chartArea": {
          "height": "100%",
          "left": 0,
          "top": 0,
          "width": "100%"
        },
        "colors": ["#FFA6A6", "#B1F0AF", "#FFED93", "#E8E8E8"],
        "enableInteractivity": false,
        "height": 130,
        "legend": {
          "position": "right",
          "textStyle": {
            "color": "#333333",
            "fontName": "Helvetica Neue",
            "fontSize": 12
          }
        },
        "pieSliceBorderColor": "#F9F4F3",
        "pieSliceText": "none",
        "tooltip": {
          "trigger": "none"
        },
        "width": 220
      };

      var chart = new google.visualization.PieChart($("#stances-chart")[0]);
      chart.draw(data, options);
    });
  }
});
