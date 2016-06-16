var mapViewer;
var drawBox;

$(document).ready(function() {
  mapViewer = new MapViewer();
  mapViewer.setupMap({useSTKTerrain: true, geocoder: true});
  mapViewer.setHomeLocation(41.8265929, -71.4137041, 1000);
  document.getElementById('right').style.display = 'block';
  document.getElementById('right').style.visibility = 'visible';

  enableButtons(false);

  drawBox = new DrawBox();
  drawBox.init(mapViewer);

  $('.bbox.degree').on('change', function(evt){
    if (allInputsValid()) {
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
      } else {
        mapViewer.updateBoundingBox(evt);
      }
    } else {
      enableButtons(false);
      if (mapViewer.homeEntity) {
        $('.bbox.degree').each(function(index) {
          var val = $( this ).val();
          if (!val || val.length === 0 || val === "") {
            $( this ).addClass('required')
          }
        });
      }
    }
  });

  // clicklistener for the clear button
  $('#clear').on('click', function(e) {
    e.preventDefault();
    $('.bbox.degree').val('');
    mapViewer.destroyBoundingBox();
    mapViewer.homeEntity = null;
    mapViewer.viewHomeLocation();
    enableButtons(false);
    drawBox = new DrawBox();
    drawBox.init(mapViewer);
  })

  // when user presses enter while on the form, don't submit - so they can
  // see their changes in the bounding box first
  $('#mainform').on('keypress', function(e) {  //TODO actually, should bump to next field if not filled in. same in other js
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) { 
      e.preventDefault();
      document.activeElement.blur();
      return false;
    }
  });
});

function allInputsValid() {
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

function enableButtons(bool) {
  $("#submit, #clear").button({
    disabled: !bool
  });
}

function updateFormFields(values) {
  document.getElementById('id_south_d').value = values.south;
  document.getElementById('id_north_d').value = values.north;
  document.getElementById('id_east_d').value = values.east;
  document.getElementById('id_west_d').value = values.west;
  document.getElementById('id_top_d').value = values.top;
  document.getElementById('id_bottom_d').value = values.bottom;
}
