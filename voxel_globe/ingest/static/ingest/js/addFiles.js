var pendingUpload = [];
var failedFiles = [];
var pendingIcon = "{% static 'icons/' %}" + "upload_pending.png";
var progressIcon = "{% static 'icons/' %}" + "upload_progress.png";
var successIcon = "{% static 'icons/' %}" + "upload_success.png";
var failIcon = "{% static 'icons/' %}" + "upload_fail.png";
var url = '{% url "ingest:uploadEndpoint" %}';
var successesHad = 0;
var successesNeeded = 0;
var batchSize = 3;

$( "#processButton" ).button({
  disabled: true
});

$('#fileupload').fileupload({
  url : url,
  dataType : 'html',
  autoUpload: false,
  loadImageMaxFileSize: 10
  // sequentialUploads: true
});

// remove non-alphanumeric characters from the input (for use in CSS ids)
function prettify(input) {
  return input.replace(/\W/g, '');
}

function onAdd(e, data) {
  console.log("Adding image for upload...");
  successesNeeded += 1;
  pendingUpload.push(data);

  data.context = $('<div class="uploadEntry"/>').appendTo('#selectedImages');

  var img = $('<img class="file-icon" id="icon' + prettify(data.files[0].name) + '" src="' + pendingIcon + '"/>');
  var node = $('<div/>')
    .append(img)
    .append($('<span/>').text(data.files[0].name));

  node.appendTo(data.context);
  data.node = node;
}

function onSubmit(e, data) {
  console.log(data.files[0].name + " submitted...");
}

function onDone(e, data) {
  console.log('data: ' + JSON.stringify(data));
  for (var i = 0; i < data.files.length; i++) {
    console.log(data.files[i].name + " done...");
    $('#icon' + prettify(data.files[i].name)).prop("src", successIcon);
    $('#icon' + prettify(data.files[i].name)).removeAttr("title");
    successesHad += 1;

    if (successesNeeded != 0 && successesHad == successesNeeded) {
      $( "#processButton" ).button({
        disabled: false
      });
      pendingUpload = [];
      successesHad = 0;
      successesNeeded = 0;
      return;
    }
  }
  ingest(successesHad);
}

function onFail(e, data) {
  console.log(data.files[0].name + " failed...");
  $('#icon' + prettify(data.files[0].name)).prop("src", failIcon);
  $('#icon' + prettify(data.files[0].name)).prop
    ("title", "Upload failed! Try re-clicking 'Upload Selected Files'. If the problem persists, it may be because your file is too big, or the filetype is incompatible.");
  failedFiles.push(data);
}

function ingest(startIndex) {
  var filesList = [];

  // add all the files in the batch to filesList and set their icons to progressIcon
  for (var i = startIndex; i < startIndex + batchSize && i < pendingUpload.length; i++) {
    $('#icon' + prettify(pendingUpload[i].files[0].name)).prop("src", progressIcon);
    filesList.push(pendingUpload[i].files[0]);
  }

  jqXHR = $('#fileupload').fileupload('send', {files: filesList});
}

var jqXHR = $('#fileupload').fileupload('enable')
  .on('fileuploadadd', onAdd)
  .on('fileuploadsubmit', onSubmit)
  .on('fileuploaddone', onDone)
  .on('fileuploadfail', onFail);

$('#fakeUpload').click(function (e) {
  $( "#processButton" ).button({
    disabled: true
  });
  $('#fileupload').click();
})

$('#doIngest').click(function (e) {
  /*if (failedFiles.length != 0) {
    for (var i = 0; i < failedFiles.length; i++) {
      pendingUpload.push(failedFiles[i]);
    }  // ACTUALLY wait no because these files are still in the pending upload list
    // that's why my print statements are printing doubly for the one that failed...
    pendingUpload.push()
    $('#fileupload').fileupload('send', {files: failedFiles});
  }*/

  // if there are no files pending upload, do nothing
  if (pendingUpload.length == 0) {
    return;
  }

  // call the ingest function with starting index 0
  ingest(successesHad);
});

$('#tempAbort').click(function (e) {
  if (jqXHR) {
    jqXHR.abort();
  }
})

$('#clearButton').click(function (e) {
  // if an upload is in progress, abort it
  if (jqXHR) {
    jqXHR.abort();
  }

  // reset the pendingUpload list and the DOM list
  pendingUpload = [];
  $('#selectedImages').html("");

  // disable the process button (since there are no files to process)
  $( "#processButton" ).button({
    disabled: true
  });
});

$('#processButton').click(function (e) {
  document.forms['ingestfolder'].submit()
  //AEN: Yeah, I don't know your jquery magic
});



















var pendingUpload = [];
var pendingIcon = "{% static 'ingest/icons/' %}" + "upload_pending.png";
var successIcon = "{% static 'ingest/icons/' %}" + "upload_success.png";
var failIcon = "{% static 'ingest/icons/' %}" + "upload_fail.png";
var url = '{% url "ingest:uploadEndpoint" %}'

var successesHad = 0;
var successesNeeded = 0;

$(document).ready(function () {
  $( "#processButton" ).button({
    disabled: true
  });

  $('#fakeUpload').click(function (e) {
    $('#fileupload').click(); 
  })

  $('#doIngest').click(function (e) {
    for (var i = 0; i < pendingUpload.length; i++) {
      console.log("Uploading file " + i);
      pendingUpload[i].submit();
    }
  });

  $('#clearButton').click(function (e) {
    console.log('clear button')
    pendingUpload = [];
    $( "#processButton" ).button({
      disabled: true
    });
    $('#selectedImages').html("");
  });

  $('#processButton').click(function (e) {
    console.log('process button')
    document.forms['ingestfolder'].submit()
    //AEN: Yeah, I don't know your jquery magic
  });

});

$('#fileupload').fileupload({ 
  url : url,
  dataType : 'html', 
  autoUpload: false 
});

$('#fileupload').fileupload('enable')
  .on('fileuploadadd', function (e, data) {
    console.log("Adding image for upload...");
    data.id = pendingUpload.length;
    successesNeeded += 1;
    pendingUpload.push(data);
    data.context = $('<div class="uploadEntry"/>').appendTo('#selectedImages');
    var img = $('<img id="icon' + data.id + '" src="' + pendingIcon + '"/>');
    var node = $('<div/>')
            .append(img)
                .append($('<span/>').text(data.files[0].name));
    node.appendTo(data.context);
    data.node = node;
  }).on('fileuploadsubmit', function(e, data) {
    console.log(data + " submitted...");
  }).on('fileuploaddone', function(e, data) {
    console.log(data + " done...");
    $('#icon' + data.id).prop("src", successIcon);
    successesHad += 1;

    var idx = pendingUpload.indexOf(data);
    if (idx > -1) {
      pendingUpload.splice(idx, 1);
      console.log('pendingUpload: ' + pendingUpload)
    }
    // TODO i think this bit should fix the bug where it tries to re-upload all files if only one fails, but not sure. how to test?
    // also, it might be really slow on large file lists -- not sure of the runtimes of indexOf and splice

    if (successesNeeded != 0 && successesHad == successesNeeded) {
      pendingUpload = [];
      console.log('all success!')
      $( "#processButton" ).button({
        disabled: false
      });
    }
  }).on('fileuploadfail', function(e, data) {
    console.log(data + " failed...");
    $('#icon' + data.id).prop("src", failIcon);    
  });
        












