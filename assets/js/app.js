var $ = require("jquery");
var dt = require("datatables.net")(window, $);

// Users datatable
$(document).ready(function () {
  $("#users-datatable").DataTable({
    language: {
      url: "../static/datatables.es-ES.json",
    },
    // Disable sorting on the 7th column (actions)
    columnDefs: [
      {
        searchable: false,
        orderable: false,
        targets: 7,
      },
    ],
  });
});

// Residents datatable
$(document).ready(function () {
  $("#residents-datatable").DataTable({
    language: {
      url: "../static/datatables.es-ES.json",
    },
    // Disable sorting on the 4th column (actions)
    columnDefs: [
      {
        searchable: false,
        orderable: false,
        targets: 3,
      },
    ],
  });
});

// Medications datatable
$(document).ready(function () {
  $("#medications-datatable").DataTable({
    language: {
      url: "../static/datatables.es-ES.json",
    },
    // Disable sorting on the 2nd and 3rd column (presentations, actions)
    columnDefs: [
      {
        searchable: false,
        orderable: false,
        targets: [1, 2],
      },
    ],
  });
});

// pillbox datatable
$("#pillbox-datatable").DataTable({
  language: {
    url: "../static/datatables.es-ES.json",
  },
  // Disable sorting on the 2nd and 3rd column (presentations, actions)
  columnDefs: [

    { 
      "witdh": "1%",
      "targets": 0,
    },
  ],
});


// stock datatable
$("#stock-datatable").DataTable({
  language: {
    url: "../static/datatables.es-ES.json",
  },
  // Disable sorting on the 2nd and 3rd column (presentations, actions)
  columnDefs: [

    { 
      "witdh": "1%",
      "targets": 0,
    },
  ],
});

// Clone form (to dynamically add forms)
$(document).ready(function () {
  // create_medication.html -> add presentation form
 
  $("#add_presentation").on("click", function () {
    const selector = "#forms_container:last";
    const type = "form";

    cloneForm(selector, type);
  });

  function cloneForm(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $("#id_" + type + "-TOTAL_FORMS").val();
    newElement.find(":input").each(function () {
      var name = $(this)
        .attr("name")
        .replace("-" + (total - 1) + "-", "-" + total + "-");
      var id = "id_" + name;      
      $(this).attr({ name: name, id: id }).val("").removeAttr("checked");
    });
    newElement.find("label").each(function () {
      var newFor = $(this)
        .attr("for")
        .replace("-" + (total - 1) + "-", "-" + total + "-");
      $(this).attr("for", newFor);
    });
    total++;
    $("#id_" + type + "-TOTAL_FORMS").val(total);
    console.log(newElement);
    $(selector).after(newElement);
  }
});


