function BuildVoxelWorldMain() {}

BuildVoxelWorldMain.prototype.initialize = function() {
  var that = this;
  that.origin = [0,0,0];
  that.initialData;
  // set the text for the help tooltips
  that.setHelpTooltips();

  if ($('#id_image_set').val()) {
    $('#message_helper')[0].innerHTML = 'Loading...';
    $.get("/meta/rest/auto/imageset/"+$('#id_image_set').val(), 
      that.set_from_image, 'json');
  } else {
    // reset and submit should be disabled until the user selects images or scene
    that.enableButtons(false);

    // disable camera set and scene until the user selects a field
    $('#id_camera_set').prop('disabled', true);
    $('#id_scene').prop('disabled', true);
  }

  // on change to either dropdown, load the rest of the form
  $('#id_image_set').change(function(){
    $('#message_helper')[0].innerHTML = 'Loading...';
    $.get("/meta/rest/auto/imageset/"+$('#id_image_set').val(), 
      that.set_from_image, 'json');
  });

  $('#id_scene').change(function(){
    $('#message_helper')[0].innerHTML = 'Loading...';
    $.get("/meta/rest/auto/scene/"+$('#id_scene').val(), function(data) {
      that.initialData = data;
      that.set_from_scene(data);
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
    if (that.allFieldsValid()) {
      that.enableButtons(true);
    }
    if ($("#id_camera_set").val()) {
      $("#id_camera_set").removeClass('required');
    }
  });

  // on change to either form, update the other form, and update the bounding
  // box visually
  $('.bbox.meter').on('change', function(evt){
    that.update_bbox_degree();
    mapViewer.updateBoundingBox(evt);
    if (that.allFieldsValid()) {
      that.enableButtons(true);
    }
  });

  $('.bbox.degree').on('change', function(evt){
    that.update_bbox_meter();
    mapViewer.updateBoundingBox(evt);
    if (that.allFieldsValid()) {
      that.enableButtons(true);
    }
  });

  // clicklistener for the reset button
  $('#reset').on('click', function(e) {
    e.preventDefault();
    if (that.initialData) {
      that.set_from_scene(that.initialData);
    }
  });

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
    if (!that.allFieldsValid()) {
      e.preventDefault();
      that.markRequiredFields();
    }
  });

  // listen for changes on any input or select field to remove the red border
  // if their value is valid
  $('select, input').on('change', function(e) {
    if ($(this).val()) {
      $(this).removeClass('required');
    }
  });
}

BuildVoxelWorldMain.prototype.update_bbox_meter = function(){
  var that = this;
  var bb0 =  global_to_local(parseFloat($('#id_west_d').val()), 
                         parseFloat($('#id_south_d').val()), 
                         parseFloat($('#id_bottom_d').val()), 
                         that.origin[0], that.origin[1], that.origin[2])
  var bb1 =  global_to_local(parseFloat($('#id_east_d').val()), 
                         parseFloat($('#id_north_d').val()), 
                         parseFloat($('#id_top_d').val()), 
                         that.origin[0], that.origin[1], that.origin[2])

  $('#id_west_m').val(bb0[0]);
  $('#id_south_m').val(bb0[1]);
  $('#id_bottom_m').val(bb0[2]);
  $('#id_east_m').val(bb1[0]);
  $('#id_north_m').val(bb1[1]);
  $('#id_top_m').val(bb1[2]);
  $('#id_voxel_size_m').val($('#id_voxel_size_d').val());
  $('.bbox').removeClass('required');
};

BuildVoxelWorldMain.prototype.update_bbox_degree = function(){
  var that = this;
  var bb0 =  local_to_global(parseFloat($('#id_west_m').val()), 
                         parseFloat($('#id_south_m').val()), 
                         parseFloat($('#id_bottom_m').val()), 
                         that.origin[0], that.origin[1], that.origin[2])
  var bb1 =  local_to_global(parseFloat($('#id_east_m').val()), 
                         parseFloat($('#id_north_m').val()), 
                         parseFloat($('#id_top_m').val()), 
                         that.origin[0], that.origin[1], that.origin[2])

  $('#id_south_d').val(bb0[0]); 
  $('#id_west_d').val(bb0[1]);
  $('#id_bottom_d').val(bb0[2]);
  $('#id_north_d').val(bb1[0]);
  $('#id_east_d').val(bb1[1]);
  $('#id_top_d').val(bb1[2]);
  $('#id_voxel_size_d').val($('#id_voxel_size_m').val())
  $('.bbox').removeClass('required');
};

BuildVoxelWorldMain.prototype.set_from_image = function(data) {
  var that = this;
  $.ajax({
    type: "GET",
    url: "/meta/rest/auto/cameraset/?images=" + $("#id_image_set").val(),
    success: function(cameraset) {
      $('#id_camera_set').val(cameraset[0].id);
      $('#id_camera_set').prop('disabled', false);
    }
  })

  if (!data['scene']) {
    main.enableButtons(false);
    $("#id_scene").val(null);
    $("#id_scene").prop('disabled', true);
    $("#bbox_degree, #bbox_meter, #bbox_unit, #right").hide();
    $("#message_helper").html("Unable to load scene data for the image set you have selected.")
    return;
  }

  $('#id_scene').val(data['scene']);
  $('#id_scene').prop('disabled', false);
  $('#message_helper')[0].innerHTML = '';
  $('#id_scene').trigger('change');
}

BuildVoxelWorldMain.prototype.set_from_scene = function(data) {
  var that = this;

  if (data.length == 0) {
    $("#message_helper").html("Unable to load scene data for the image set you have selected.")
    return;
  }

  that.origin = data['origin']['coordinates'];
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

    that.update_bbox_degree();

    var values = {
      'south': parseFloat($('#id_south_d').val()),
      'west': parseFloat($('#id_west_d').val()),
      'bottom': parseFloat($('#id_bottom_d').val()),
      'north': parseFloat($('#id_north_d').val()),
      'east': parseFloat($('#id_east_d').val()),
      'top': parseFloat($('#id_top_d').val()),
    }

    $("#right").show();
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

    $("#right").hide();
  }
  
  // enable the reset and submit buttons now, and hide the help tooltips
  if (that.allFieldsValid()) {
    that.enableButtons(true);
  } else {
    that.enableReset(true);
    that.enableSubmit(false);
  }

  $('#message_helper')[0].innerHTML  = '';
}

BuildVoxelWorldMain.prototype.updateFormFields = function(values) {
  document.getElementById('id_south_d').value = values.south;
  document.getElementById('id_north_d').value = values.north;
  document.getElementById('id_east_d').value = values.east;
  document.getElementById('id_west_d').value = values.west;
  document.getElementById('id_top_d').value = values.top;
  document.getElementById('id_bottom_d').value = values.bottom;
  main.update_bbox_meter();
}

BuildVoxelWorldMain.prototype.setHelpTooltips = function() {
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
BuildVoxelWorldMain.prototype.allFieldsValid = function() {
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

BuildVoxelWorldMain.prototype.markRequiredFields = function() {
  var that = this;
  that.enableSubmit(false);
  $('input, #id_image_set, #id_camera_set, #id_scene').each(function(index) {
    if ($(this).is(':visible')) {
      var val = $( this ).val();
      if (!val || val.length === 0 || val === "") {
        $( this ).addClass('required');
      }
    }
  });
}

BuildVoxelWorldMain.prototype.enableButtons = function(bool) {
  $("#submit, #reset").button({
    disabled: !bool
  });
}

BuildVoxelWorldMain.prototype.enableSubmit = function(bool) {
  $("#submit").button({
    disabled: !bool
  });
}

BuildVoxelWorldMain.prototype.enableReset = function(bool) {
  $("#reset").button({
    disabled: !bool
  });
}
