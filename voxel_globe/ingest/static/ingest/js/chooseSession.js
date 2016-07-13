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

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var sessions;

function loadSession(sessionNdx) {
  console.log("Loading existing session..." + sessions[sessionNdx].name);
  // console.log(sessions[sessionNdx].id);
  // TODO: Figure out how to hook into the Django stuff to load an existing session
  load(sessions[sessionNdx].id);
  //window.open("{% url "ingest:addFiles" %}?upload="+sessions[sessionNdx].id,'_top');
}

function createSession() {
  var newName = $('#newSessionId').val();
  var uploadCategory = $('input[name="uploadCategory"]:checked').val();

  if (newName.length == 0) {
    $('#newSessionId').addClass('required');
    $('#newSessionId').keyup(function(e) {
      if ($('#newSessionId').val().length != 0) {
        $('#newSessionId').removeClass('required');
        $('#newSessionId').off('keyup');
      }
    })
    return;
  }

  // Check the name against the other sessions...
  for (var i = 0; i < sessions.length; i++) {
    if (sessions[i].name == newName) {
      alert("There is already an upload with name " + newName);
      return;
    }
  }

  // Otherwise we are OK, go ahead and create the upload session
  if (uploadCategory == "image") {
    var metadata_type = $('#metadata_type').val();
    var payload_type = $('#payload_type').val();
    console.log("Attempting to create " + newName +
      "," + metadata_type + ',' + payload_type);

    $.post("rest/uploadsession/", { name : newName,
      metadata_type : metadata_type, payload_type : payload_type }, function (data) {
      console.log("Created session..." + newName);
      load(data.id);

    }).fail( function(e) {
      alert("Unable to create the new upload: " + e.responseJSON.name[0]);
      prompt.dialog( "close" );
    });

  } else if (uploadCategory == "controlPoint") {
    var controlpoint_type = $('#controlpoint_type').val();
    console.log("Attempting to create " + newName +
     "," + controlpoint_type);

    $.post("/apps/ingest/rest/uploadsession/", { name : newName,
      metadata_type : 'None', payload_type : 'None',
      upload_types : JSON.stringify({controlpoint_type:controlpoint_type}) },  function (data) {
      console.log("Created session..." + newName);
      load(data.id);
    }).fail( function(e) {
      alert("Unable to create the new upload: " + e);
      prompt.dialog( "close" );
    });
  }
}

$(document).ready(function() {
  $("#ctrl-pt-options").hide();
  
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  $.get("rest/uploadsession/", function (data) {
    $("#availableSessions").html("");
    sessions = data;

    if (sessions.length === 0) {
      $("#orSelectNew").hide();
      $("#availableSessions").hide();
      $("#oldSession").hide();
      return;
    } else {
      $("#orSelectNew").show();
      $("#availableSessions").show();
      $("#oldSession").show();
    }

    for (var i = 0; i < sessions.length; i++) {
      $("#availableSessions").append('<option value="' + 
        i + '">' + sessions[i].name + '</option>');
    }
    console.log(data.length + " sessions were loaded.");

    $("#oldSession").click(function() {
      var i = $('#availableSessions').val();
      loadSession(i);
    })
  });

  prompt = $('#newSessionDialog').dialog({
    autoOpen : false, 
    modal : true,
    autoResize : true,
    show: { effect: "drop", direction: "up", duration: 100 },
    hide: { effect: "drop", direction: "up", duration: 100 },
    title: "New Session",
    bgiframe: true,
    dialogClass: 'withDropShadow',
    open: function(){
      $('.ui-widget-overlay').bind('click',function(){
        $('#newSessionDialog').dialog('close');
      })
    },
    buttons: {
      "Create the Session": createSession,
      "Cancel": function() {
        prompt.dialog( "close" );
      }
    }


  });

  $('#newSession').on('click', function () {
    prompt.dialog("open");
  });

  $('input:radio').on('click', function(e) {
    if (e.currentTarget.name != "uploadCategory") {
      return;
    }
    var uploadCategory = e.currentTarget.value;
    if (uploadCategory == "image") {
      $("#img-options").show();
      $("#ctrl-pt-options").hide();
    } else if (uploadCategory == "controlPoint") {
      $("#img-options").hide();
      $("#ctrl-pt-options").show();
    }
  });
});
