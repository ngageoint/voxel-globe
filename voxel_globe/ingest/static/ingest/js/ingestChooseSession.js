var prompt;

$(document).ready(function () {
  var csrftoken = getCookie('csrftoken');

  prompt = $('#newSessionDialog').dialog({autoOpen : false, modal : true,
    title: "New Session",
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
    for (var i = 0; i < sessions.length; i++) {
      $("#availableSessions").append('<button style="" onclick="loadSession(' + i + ')">Upload ' + sessions[i].name + '</button></br>');
    }
    console.log(data.length + " sessions were loaded.");
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

function createSession() {
  var newName = $('#newSessionId').val();
  var metadata_type = $('#metadata_type').val();
  var payload_type = $('#payload_type').val();
  // Check the name against the other sessions...
  for (var i = 0; i < sessions.length; i++) {
    if (sessions[i].name == newName) {
      alert("There is already an upload with name " + newName);
      return;
    }
  }
  // Otherwise we are OK, go ahead and create the upload session
  console.log("Attempting to create " + newName +
     "," + metadata_type + ',' + payload_type);
  $.post("rest/uploadsession/", { name : newName,
    metadata_type : metadata_type, payload_type : payload_type }, function (data) {
    console.log("Created session..." + newName);
    prompt.dialog( "close" );
    window.open("addFiles?upload=" + data['id'], '_top');
  }).fail( function(e) {
    alert("Unable to create the new upload: " + e);
    prompt.dialog( "close" );
  });
}






















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

function createSession() {
  var newName = $('#newSessionId').val();
  var metadata_type = $('#metadata_type').val();
  var payload_type = $('#payload_type').val();
  // Check the name against the other sessions...
  for (var i = 0; i < sessions.length; i++) {
    if (sessions[i].name == newName) {
      alert("There is already an upload with name " + newName);
      return;
    }
  }
  // Otherwise we are OK, go ahead and create the upload session
  console.log("Attempting to create " + newName +
     "," + metadata_type + ',' + payload_type);
  $.post("rest/uploadsession/", { name : newName,
    metadata_type : metadata_type, payload_type : payload_type }, function (data) {
    console.log("Created session..." + newName);
    prompt.dialog( "close" );
    window.open("{% url "ingest:addFiles" %}?upload="+data['id'],'_top');
  }).fail( function(e) {
    alert("Unable to create the new upload: " + e);
    prompt.dialog( "close" );
  });
}

prompt = $('#newSessionDialog').dialog({autoOpen : false, modal : true,
  title: "New Session",
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