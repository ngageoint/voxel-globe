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
  $('#id_camera_set').val(data.id);
  $('#id_camera_set, #id_scene').prop('disabled', false);
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
    mapViewer.viewHomeLocation();

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

    document.getElementById('right').style.display = 'none';
  }
  
  // enable the reset and submit buttons now, and hide the help tooltips
  if (allFieldsValid()) {
    enableButtons(true);
  } else {
    enableReset(true);
    enableSubmit(false);
  }

  $('#message_helper')[0].innerHTML  = '';
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
    ' id="image_set_help" class="ui-icon ui-icon-help">"</span>');
  $('#id_camera_set').after('<span style="display: inline-block"' + 
    ' id="camera_set_help" class="ui-icon ui-icon-help"></span>');
  $('#id_scene').after('<span style="display: inline-block"' + 
    ' id="scene_help" class="ui-icon ui-icon-help"></span>');
  $("#image_set_help, #scene_help, #camera_set_help").css('cursor','pointer');

  $($('#image_set_help').parent()).tooltip({
      items: '#image_set_help',
      content: "From the image sets you have uploaded, choose which dataset " +
      "to use for voxel world processing."
  });

  $($('#camera_set_help').parent()).tooltip({
    items: '#camera_set_help',
    content: "Select the camera set corresponding to the image set."
  });

  $($('#scene_help').parent()).tooltip({
      items: '#scene_help',
      content: "When selecting a scene origin to use, it's best to select " +
      " the same origin the image data is associated with already."
  });
}

// check that all form fields are valid
var allFieldsValid = function() {
  var ret = true;
  $('input, #id_image_set, #id_camera_set, #id_scene').each(function(index) {
    if ($(this).is(':visible')) {
      var val = $( this ).val();
      if (!val || val.length === 0 || val === "") {
        ret = false;
      } else {
        $( this ).removeClass('required');
      }
    }
  });
  return ret;
}

function markRequiredFields() {
  enableSubmit(false);
  $('input, #id_image_set, #id_camera_set, #id_scene').each(function(index) {
    if ($(this).is(':visible')) {
      var val = $( this ).val();
      if (!val || val.length === 0 || val === "") {
        $( this ).addClass('required');
      }
    }
  });
}

function enableButtons(bool) {
  $("#submit, #reset").button({
    disabled: !bool
  });
}

function enableSubmit(bool) {
  $("#submit").button({
    disabled: !bool
  });
}

function enableReset(bool) {
  $("#reset").button({
    disabled: !bool
  });
}

$(document).ready(function(){
  // set the text for the help tooltips
  setHelpTooltips();

  // reset and submit should be disabled until the user selects images or scene
  enableButtons(false);

  // disable camera set and scene until the user selects a field
  $('#id_camera_set').prop('disabled', true);
  $('#id_scene').prop('disabled', true);

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
  });

  // on change to voxel size in either form, update the other form
  $('#id_voxel_size_m').on('change', function(evt){
    $('#id_voxel_size_d').val($('#id_voxel_size_m').val());
  });

  $('#id_voxel_size_d').on('change', function(evt){
    $('#id_voxel_size_m').val($('#id_voxel_size_d').val());
  });

  $('#id_camera_set').on('change', function(evt){
    if (allFieldsValid()) {
      enableButtons(true);
    }
    if ($("#id_camera_set").val()) {
      $("#id_camera_set").removeClass('required');
    }
  });

  // on change to either form, update the other form, and update the bounding
  // box visually
  $('.bbox.meter').on('change', function(evt){
    update_bbox_degree();
    mapViewer.updateBoundingBox(evt);
    if (allFieldsValid()) {
      enableButtons(true);
    }
  });

  $('.bbox.degree').on('change', function(evt){
    update_bbox_meter();
    mapViewer.updateBoundingBox(evt);
    if (allFieldsValid()) {
      enableButtons(true);
    }
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
      return $(e.target).blur().focus();
    }
  });

  $("form").on("submit", function(e) {
    if (!allFieldsValid()) {
      e.preventDefault();
      markRequiredFields();
    }
  });
});