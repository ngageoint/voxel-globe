var mapViewer;
var drawBox;

$(document).ready(function() {
  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true, geocoder: true});
  //mapViewer.setHomeLocation(41.8265929, -71.4137041, 1000);
  mapViewer.setHomeLocation(180,-2, 1000);
  document.getElementById('right').style.display = 'block';
  document.getElementById('right').style.visibility = 'visible';

  $("#id_name").width($("#id_south_d").width());

  enableButtons(false);

  drawBox = new DrawBox();
  drawBox.init(mapViewer);

  $('.bbox.degree').on('change', function(evt){
    if (allButNameValid()) {
      enableClear(true);
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
      markRequiredFields();
    }
  });

  document.getElementById('id_name').addEventListener('keyup', function(evt) {
    if (allInputsValid()) {
      enableButtons(true);
    }
  });

  // clicklistener for the clear button
  $('#clear').on('click', function(e) {
    e.preventDefault();
    $('.bbox.degree').val('');
    mapViewer.destroyBoundingBox();
    mapViewer.homeEntity = null;
    //mapViewer.viewHomeLocation();
    enableButtons(false);
    drawBox = new DrawBox();
    drawBox.init(mapViewer);
  });

  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  $('#submit').on('click', submitRequest);
  // when user presses enter while on the form, don't submit - so they can
  // see their changes in the bounding box first
  $('#mainform').on('keypress', function(e) {  //TODO actually, should bump to next field if not filled in. same in other js
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) { 
      e.preventDefault();
      return $(e.target).blur().focus();
    }
  });
});

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function allInputsValid() {
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

function allButNameValid() {
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

function markRequiredFields() {
  enableSubmit(false);
  if (mapViewer.homeEntity) {
    $('.bbox.degree, #id_name').each(function(index) {
      var val = $( this ).val();
      if (!val || val.length === 0 || val === "") {
        $( this ).addClass('required');
      }
    });
  }
}

function enableButtons(bool) {
  $("#submit, #clear").button({
    disabled: !bool
  });
}

function enableSubmit(bool) {
  $("#submit").button({
    disabled: !bool
  })
}

function enableClear(bool) {
  $("#clear").button({
    disabled: !bool
  })
}

function updateFormFields(values) {
  document.getElementById('id_south_d').value = values.south;
  document.getElementById('id_north_d').value = values.north;
  document.getElementById('id_east_d').value = values.east;
  document.getElementById('id_west_d').value = values.west;
  document.getElementById('id_top_d').value = values.top;
  document.getElementById('id_bottom_d').value = values.bottom;
}

function submitRequest(e) {
  e.preventDefault();
  if (!allInputsValid()) {
    markRequiredFields();
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
