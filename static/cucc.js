$(document).ready(function() {
  $("#varazslat").submit(function() {
    $.get("/etr/kurzustabla", $(this).serialize(), addhozza, "json");

    return false;
  })
  
})


function addhozza(data) {
  $.each(data, function() {
    console.log(this.cim)
    $("<li />", {
    }).appendTo("#kurzustabla");
    $("<input />", {
      id: this.kurzusid,
      "name": "kurzus",
      value: this.kurzusid,
      type: "checkbox",
      change: function() {
        if ($(this).is(":checked")) {
          $(this).parent().addClass("selected")
        } else {
          $(this).parent().removeClass("selected")
        } 
      }
    }).appendTo("#kurzustabla li:last")
    $("<label />", {
      "for": this.kurzusid,
      html: this.kurzuskod + " " + this.cim
    }).appendTo("#kurzustabla li:last")
  })
    $("<button/>", {
          "html": "mutasd", 
          "click": function() { alert("bla"); return false }
        }).appendTo("#kurzustabla")
    $("#login").slideUp()
    
}

function kozoskurzusok() {
  alert(bla)
}
