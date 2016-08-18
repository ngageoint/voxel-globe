function CreateSiteMain() {}

CreateSiteMain.prototype.initialize = function() {
  var that = this;
  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true, geocoder: true});
  mapViewer.viewHomeLocation();  // should be stored in a cookie
  document.getElementById('right').style.display = 'block';
  document.getElementById('right').style.visibility = 'visible';

  if (that.allButNameValid()) {
    var values = {
      'south': parseFloat($('#id_south_d').val()),
      'west': parseFloat($('#id_west_d').val()),
      'bottom': parseFloat($('#id_bottom_d').val()),
      'north': parseFloat($('#id_north_d').val()),
      'east': parseFloat($('#id_east_d').val()),
      'top': parseFloat($('#id_top_d').val()),
    }
    mapViewer.createBoundingBox(values);
    mapViewer.viewHomeLocation();
    if (that.allInputsValid()) {
      that.enableSubmit(true);
    } else {
      that.enableSubmit(false);
    }
    that.toggleMapButtons('clear');
  } else {
    that.enableSubmit(false);
  }

  $('.bbox.degree').on('change', function(evt){
    if (that.allInputsValid()) {
      that.enableSubmit(true);
    } else {
      that.enableSubmit(false);
    }
    
    if (that.allButNameValid()) {
      if (!mapViewer.homeEntity) {
        if (drawBox) {
          drawBox.destroy();
        }
        var values = {
          'south': parseFloat($('#id_south_d').val()),
          'west': parseFloat($('#id_west_d').val()),
          'bottom': parseFloat($('#id_bottom_d').val()),
          'north': parseFloat($('#id_north_d').val()),
          'east': parseFloat($('#id_east_d').val()),
          'top': parseFloat($('#id_top_d').val()),
        }
        mapViewer.createBoundingBox(values);
        mapViewer.viewHomeLocation();
      } else {
        mapViewer.updateBoundingBox(evt);
      }
    } else {
      that.markRequiredFields();
    }
  });

  $("#id_name").width($("#id_south_d").width());

  $("#id_name").on('keyup', function(evt) {
    if (that.allInputsValid()) {
      that.enableSubmit(true);
    } else {
      that.enableSubmit(false);
    }
  })

  $('#draw').on('click', function(e) {
    drawBox = new DrawBox();
    drawBox.init(mapViewer);
    that.toggleMapButtons('cancel');
  });

  $('#cancel').on('click', function(e) {
    drawBox.destroy();
    that.toggleMapButtons('draw');
  })

  // clicklistener for the clear button
  $('#clear').on('click', function(e) {
    e.preventDefault();
    $('.bbox.degree').val('');
    mapViewer.destroyBoundingBox();
    mapViewer.homeEntity = null;
    //mapViewer.viewHomeLocation();
    that.enableSubmit(false);
    that.toggleMapButtons('draw');
  });

  $('#submit').on('click', submitRequest);
  // when user presses enter while on the form, don't submit - so they can
  // see their changes in the bounding box first
  $('#mainform').on('keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) { 
      e.preventDefault();
      return $(e.target).blur().focus();
    }
  });
}

CreateSiteMain.prototype.allInputsValid = function() {
  var ret = true;
  $('.bbox.degree, #id_name').each(function(index) {
    var val = $( this ).val();
    if (!val || val.length === 0 || val === "") {
      ret = false;
    } else {
      $( this ).removeClass('required');
    }
  });
  return ret;
}

CreateSiteMain.prototype.allButNameValid = function() {
  var ret = true;
  $('.bbox.degree').each(function(index) {
    var val = $( this ).val();
    if (!val || val.length === 0 || val === "") {
      ret = false;
    } else {
      $( this ).removeClass('required');
    }
  });
  return ret;
}

CreateSiteMain.prototype.markRequiredFields = function() {
  var that = this;
  that.enableSubmit(false);
  if (mapViewer.homeEntity) {
    $('.bbox.degree, #id_name').each(function(index) {
      var val = $( this ).val();
      if (!val || val.length === 0 || val === "") {
        $( this ).addClass('required');
      }
    });
  }
}

CreateSiteMain.prototype.enableSubmit = function(bool) {
  $("#submit").button({
    disabled: !bool
  })
}

CreateSiteMain.prototype.toggleMapButtons = function(button) {
  $(".map-button").hide();
  $("#" + button).show();
}

var updateFormFields = function(values) {
  document.getElementById('id_south_d').value = values.south;
  document.getElementById('id_north_d').value = values.north;
  document.getElementById('id_east_d').value = values.east;
  document.getElementById('id_west_d').value = values.west;
  document.getElementById('id_top_d').value = values.top;
  document.getElementById('id_bottom_d').value = values.bottom;
  if (main.allInputsValid()) {
    main.enableSubmit(true);
  } else {
    main.enableSubmit(false);
  }
}

var submitRequest = function(e) {
  var that = main;
  e.preventDefault();
  if (!that.allInputsValid()) {
    that.markRequiredFields();
    return;
  }

  var name = document.getElementById('id_name').value;
  var s = parseFloat($('#id_south_d').val());
  var w = parseFloat($('#id_west_d').val());
  var b = parseFloat($('#id_bottom_d').val());
  var n = parseFloat($('#id_north_d').val());
  var e = parseFloat($('#id_east_d').val());
  var t = parseFloat($('#id_top_d').val());

  $.ajax({
    type: "POST",
    url: "/meta/rest/auto/sattelsite/",
    data: JSON.stringify({
      name : name,
      _attributes : {'web': true},
      bbox_min : {
        type : "Point",
        coordinates : [w, s, b]
      },
      bbox_max : {
        type : "Point",
        coordinates : [e, n, t]
      }
    }),

    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(data) {
      var csrftoken = getCookie('csrftoken');
      $.redirect('/apps/order/create_site/', {
        'csrfmiddlewaretoken': csrftoken, 
        'sattel_site_id': data.id
      });
    },
    error: function(msg) {
      alert(msg.responseText);  // TODO
    }
  });
}
