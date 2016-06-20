// Global functions

var origin = [0,0,0];
var initialData;
var mapViewer;

var update_bbox_meter = function(){
  bb0 =  global_to_local(parseFloat($('#id_west_d').val()), 
                         parseFloat($('#id_south_d').val()), 
                         parseFloat($('#id_bottom_d').val()), 
                         origin[0], origin[1], origin[2])
  bb1 =  global_to_local(parseFloat($('#id_east_d').val()), 
                         parseFloat($('#id_north_d').val()), 
                         parseFloat($('#id_top_d').val()), 
                         origin[0], origin[1], origin[2])

  $('#id_west_m').val(bb0[0]);
  $('#id_south_m').val(bb0[1]);
  $('#id_bottom_m').val(bb0[2]);
  $('#id_east_m').val(bb1[0]);
  $('#id_north_m').val(bb1[1]);
  $('#id_top_m').val(bb1[2]);
  $('#id_voxel_size_m').val($('#id_voxel_size_d').val());
};

var update_bbox_degree = function(){
  bb0 =  local_to_global(parseFloat($('#id_west_m').val()), 
                         parseFloat($('#id_south_m').val()), 
                         parseFloat($('#id_bottom_m').val()), 
                         origin[0], origin[1], origin[2])
  bb1 =  local_to_global(parseFloat($('#id_east_m').val()), 
                         parseFloat($('#id_north_m').val()), 
                         parseFloat($('#id_top_m').val()), 
                         origin[0], origin[1], origin[2])

  $('#id_south_d').val(bb0[0]); 
  $('#id_west_d').val(bb0[1]);
  $('#id_bottom_d').val(bb0[2]);
  $('#id_north_d').val(bb1[0]);
  $('#id_east_d').val(bb1[1]);
  $('#id_top_d').val(bb1[2]);
  $('#id_voxel_size_d').val($('#id_voxel_size_m').val())
};

var set_from_image = function(data) {
  $('#id_scene').val(data['scene']);
  $('#message_helper')[0].innerHTML = '';
  $('#id_scene').trigger('change');
}

var set_from_scene = function(data) {
  origin = data['origin']['coordinates'];

  if (data['geolocated']) {
    $('#bbox_degree').css('display', 'block');
    $('#bbox_meter').css('display', 'block');
    $('#bbox_unit').css('display', 'none');

    $('#id_south_m').val(data['bbox_min']['coordinates'][0]);
    $('#id_west_m').val(data['bbox_min']['coordinates'][1]);
    $('#id_bottom_m').val(data['bbox_min']['coordinates'][2]);

    $('#id_north_m').val(data['bbox_max']['coordinates'][0]);
    $('#id_east_m').val(data['bbox_max']['coordinates'][1]);
    $('#id_top_m').val(data['bbox_max']['coordinates'][2]);

    $('#id_voxel_size_m').val(data['default_voxel_size']['coordinates'][0]);

    update_bbox_degree();

    var values = {
      'south': parseFloat($('#id_south_d').val()),
      'west': parseFloat($('#id_west_d').val()),
      'bottom': parseFloat($('#id_bottom_d').val()),
      'north': parseFloat($('#id_north_d').val()),
      'east': parseFloat($('#id_east_d').val()),
      'top': parseFloat($('#id_top_d').val()),
    }

    if (!mapViewer) {
      // set up the map viewer
      mapViewer = new MapViewer();
      mapViewer.setupMap({useSTKTerrain: true});
    }

    mapViewer.createBoundingBox(values);
    //setStep(values);

    //Clear the units fields so they can't appear valid
    $('.unit').each(function(i,x){x.value = '';})
  } else {
    $('#bbox_degree').css('display', 'none');
    $('#bbox_meter').css('display', 'none');
    $('#bbox_unit').css('display', 'block');

    $('#id_south_u').val(data['bbox_min']['coordinates'][0]);
    $('#id_west_u').val(data['bbox_min']['coordinates'][1]);
    $('#id_bottom_u').val(data['bbox_min']['coordinates'][2]);

    $('#id_north_u').val(data['bbox_max']['coordinates'][0]);
    $('#id_east_u').val(data['bbox_max']['coordinates'][1]);
    $('#id_top_u').val(data['bbox_max']['coordinates'][2]);

    $('#id_voxel_size_u').val(data['default_voxel_size']['coordinates'][0]);

    //Clear the meter and degree fields so they can't appear valid
    $('.meter').each(function(i,x){x.value = '';})
    $('.degree').each(function(i,x){x.value = '';})
  }

  $('#message_helper')[0].innerHTML  = '';
}

// TODO
// the here was to set the step value of the form elements, so for example
// the latitude would increase by 0.01 or 0.001 rather than 1. I was thinking
// of setting according to the precision of the initial data even. However,
// setting the step value from javascript makes a nasty 
// red border show up on the form in firefox (not chrome?) that I can't
// get rid of -- so will return to later if time.
var setStep = function(values) {
  // -moz-box-shadow
  // work for unit as well?
  var diff = Math.min(Math.abs(values.north - values.south), 
    Math.abs(values.east - values.west));
  var precision = Math.min(3, (diff + "").split(".")[1].length);
  var step = Math.pow(10, (0 - precision));

  $("#id_north_d").attr({"step" : step});
  $("#id_south_d").attr({"step" : step});
  $("#id_east_d").attr({"step" : step});
  $("#id_west_d").attr({"step" : step});
}

var updateFormFields = function(values) {
  document.getElementById('id_south_d').value = values.south;
  document.getElementById('id_north_d').value = values.north;
  document.getElementById('id_east_d').value = values.east;
  document.getElementById('id_west_d').value = values.west;
  document.getElementById('id_top_d').value = values.top;
  document.getElementById('id_bottom_d').value = values.bottom;
  update_bbox_meter();
}

var setHelpTooltips = function() {
  $('#id_image_set').after('<span style="display: inline-block"' + 
    ' id="image_set_help" class="ui-icon ui-icon-help"> title="help!"</span>');
  $('#id_scene').after('<span style="display: inline-block"' + 
    ' id="scene_help" class="ui-icon ui-icon-help"></span>');
  $("#image_set_help, #scene_help").css('cursor','pointer');
  $($('#image_set_help').parent()).tooltip({
      items: '#image_set_help',
      content: "From the image sets you have uploaded, choose which dataset " +
      "to use for voxel world processing."
  });
  $($('#scene_help').parent()).tooltip({
      items: '#scene_help',
      content: "When selecting a scene origin to use, it's best to select " +
      " the same origin the image data is associated with already."
  });
}

$(document).ready(function(){
  // set the text for the help tooltips
  setHelpTooltips();

  // reset and submit should be disabled until the user selects images or scene
  $("#reset, #submit").button({
    disabled: true
  });

  // on change to either dropdown, load the rest of the form
  $('#id_image_set').change(function(){
    $('#message_helper')[0].innerHTML = 'Loading...';
    $.get("/meta/rest/auto/imageset/"+$('#id_image_set').val(), 
      set_from_image, 'json');
  });

  $('#id_scene').change(function(){
    $('#message_helper')[0].innerHTML = 'Loading...';
    $.get("/meta/rest/auto/scene/"+$('#id_scene').val(), function(data) {
      initialData = data;
      set_from_scene(data);
    }, 'json');

    // enable the reset and submit buttons now, and hide the help tooltips
    $("#reset, #submit").button({ disabled: false });
    $("#image_set_help, #scene_help").hide();
  });

  // on change to voxel size in either form, update the other form
  $('#id_voxel_size_m').on('change', function(evt){
    $('#id_voxel_size_d').val($('#id_voxel_size_m').val());
  });

  $('#id_voxel_size_d').on('change', function(evt){
    $('#id_voxel_size_m').val($('#id_voxel_size_d').val());
  });

  // on change to either form, update the other form, and update the bounding
  // box visually
  $('.bbox.meter').on('change', function(evt){
    update_bbox_degree();
    mapViewer.updateBoundingBox(evt);
  });

  $('.bbox.degree').on('change', function(evt){
    update_bbox_meter();
    mapViewer.updateBoundingBox(evt);
  });

  // clicklistener for the reset button
  $('#reset').on('click', function(e) {
    e.preventDefault();
    if (initialData) {
      set_from_scene(initialData);
    }
  })

  // when user presses enter while on the form, don't submit - so they can
  // see their changes in the bounding box first
  $('form').on('keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) { 
      e.preventDefault();
      document.activeElement.blur();
      return false;
    }
  });
});