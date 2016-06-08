// Global functions

var origin = [0,0,0];
var initialData;

var update_bbox_meter = function(){
  bb0 =  global_to_local(parseFloat($('#id_west_d')[0].value), 
                         parseFloat($('#id_south_d')[0].value), 
                         parseFloat($('#id_bottom_d')[0].value), 
                         origin[0], origin[1], origin[2])
  bb1 =  global_to_local(parseFloat($('#id_east_d')[0].value), 
                         parseFloat($('#id_north_d')[0].value), 
                         parseFloat($('#id_top_d')[0].value), 
                         origin[0], origin[1], origin[2])

  $('#id_west_m')[0].value = bb0[0]
  $('#id_south_m')[0].value = bb0[1]
  $('#id_bottom_m')[0].value = bb0[2]
  $('#id_east_m')[0].value = bb1[0]
  $('#id_north_m')[0].value = bb1[1]
  $('#id_top_m')[0].value = bb1[2]
  $('#id_voxel_size_m')[0].value = $('#id_voxel_size_d')[0].value
};

var update_bbox_degree = function(){
  bb0 =  local_to_global(parseFloat($('#id_west_m')[0].value), 
                         parseFloat($('#id_south_m')[0].value), 
                         parseFloat($('#id_bottom_m')[0].value), 
                         origin[0], origin[1], origin[2])
  bb1 =  local_to_global(parseFloat($('#id_east_m')[0].value), 
                         parseFloat($('#id_north_m')[0].value), 
                         parseFloat($('#id_top_m')[0].value), 
                         origin[0], origin[1], origin[2])

  $('#id_south_d')[0].value = bb0[0]
  $('#id_west_d')[0].value = bb0[1]
  $('#id_bottom_d')[0].value = bb0[2]
  $('#id_north_d')[0].value = bb1[0]
  $('#id_east_d')[0].value = bb1[1]
  $('#id_top_d')[0].value = bb1[2]
  $('#id_voxel_size_d')[0].value = $('#id_voxel_size_m')[0].value
};

var reset = function() {
  // TODO
  // using variable initialData
  // factor out what happens below into its own function,
  // and call it again when reset gets pressed
  // alsoo, update the visual bounding box in cesium
  console.log('reset');
}

$(function(){
  $('#id_image_set').change(function(){
    $('#message_helper')[0].innerHTML = 'Loading...'
    $.get("/meta/rest/auto/imageset/"+$('#id_image_set')[0].value, function(data){
      $('#id_scene')[0].value = data['scene'];
      $('#message_helper')[0].innerHTML = '';
      $('#id_scene').trigger('change');
    }, 'json');
  });

  $('#id_scene').change(function(){
    $('#message_helper')[0].innerHTML = 'Loading...';

    $.get("/meta/rest/auto/scene/"+$('#id_scene')[0].value, function(data){

      origin = data['origin']['coordinates'];

      if (data['geolocated']) {
        $('#bbox_degree')[0].style.display = 'block';  //['visibility'] = 'visible';
        $('#bbox_meter')[0].style.display = 'block';  //['visibility'] = 'visible';
        $('#bbox_unit')[0].style.display = 'none';  //['visibility'] = 'collapse';

        $('#id_south_m')[0].value = data['bbox_min']['coordinates'][0];
        $('#id_west_m')[0].value = data['bbox_min']['coordinates'][1];
        $('#id_bottom_m')[0].value = data['bbox_min']['coordinates'][2];

        $('#id_north_m')[0].value = data['bbox_max']['coordinates'][0];
        $('#id_east_m')[0].value = data['bbox_max']['coordinates'][1];
        $('#id_top_m')[0].value = data['bbox_max']['coordinates'][2];

        $('#id_voxel_size_m')[0].value = data['default_voxel_size']['coordinates'][0];

        update_bbox_degree()
        var values = {
          'south': parseFloat($('#id_south_d')[0].value),
          'west': parseFloat($('#id_west_d')[0].value),
          'bottom': parseFloat($('#id_bottom_d')[0].value),
          'north': parseFloat($('#id_north_d')[0].value),
          'east': parseFloat($('#id_east_d')[0].value),
          'top': parseFloat($('#id_top_d')[0].value),
        }
        createBoundingBox(values);

        //Clear the units fields so they can't appear valid
        $('.unit').each(function(i,x){x.value = '';})
      } else {
        $('#bbox_degree')[0].style.display = 'block';  //['visibility'] = 'collapse';
        $('#bbox_meter')[0].style.display = 'block';  //['visibility'] = 'collapse';
        $('#bbox_unit')[0].style.display = 'none';  //['visibility'] = 'visible';

        $('#id_south_u')[0].value = data['bbox_min']['coordinates'][0];
        $('#id_west_u')[0].value = data['bbox_min']['coordinates'][1];
        $('#id_bottom_u')[0].value = data['bbox_min']['coordinates'][2];

        $('#id_north_u')[0].value = data['bbox_max']['coordinates'][0];
        $('#id_east_u')[0].value = data['bbox_max']['coordinates'][1];
        $('#id_top_u')[0].value = data['bbox_max']['coordinates'][2];

        $('#id_voxel_size_u')[0].value = data['default_voxel_size']['coordinates'][0];

        //Clear the meter and degree fields so they can't appear valid
        $('.meter').each(function(i,x){x.value = '';})
        $('.degree').each(function(i,x){x.value = '';})
      }

      $('#message_helper')[0].innerHTML  = '';
    }, 'json');

    $("#reset").button({
      disabled: false
    });
    $("#submit").button({
      disabled: false
    });
  });
});

$(document).ready(function(){
  $('#id_voxel_size_m').on('change', function(evt){
    $('#id_voxel_size_d')[0].value = $('#id_voxel_size_m')[0].value
  });
  $('#id_voxel_size_d').on('change', function(evt){
    $('#id_voxel_size_m')[0].value = $('#id_voxel_size_d')[0].value
  });
  // (todo: if I'm not wrong, voxel size change shouldn't trigger a change
  // to the bounding box on the cesium pane. but maybe?)
  $('.bbox.meter').on('change', function(evt){
    update_bbox_degree();
    updateBoundingBox(evt)
  });
  $('.bbox.degree').on('change', function(evt){
    update_bbox_meter();
    updateBoundingBox(evt)
  });

  $("#reset").button({
    disabled: true
  });
  $("#submit").button({
    disabled: true
  });

  $('#reset').on('click', function(e) {
    e.preventDefault();
    reset();
  })

  $('form').on('keypress', function(e) {
    console.log(e)
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) { 
      e.preventDefault();
      document.activeElement.blur();
      return false;
    }
  });
});