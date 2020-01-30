// Call the dataTables jQuery plugin
$(document).ready(function () {
  $('#tableDetail').DataTable({
    "order": [[6, "desc"]],
  });

  $('#recordTable').DataTable({
    "order": [[0, "desc"]],
  });
});






