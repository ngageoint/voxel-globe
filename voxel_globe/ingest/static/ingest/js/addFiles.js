var pendingUpload = [];
var failedFiles = [];
var jqXHR;
var successesHad = 0;
var successesNeeded = 0;
var batchSize = 4;


// remove non-alphanumeric characters from the input (for use in CSS ids)
function prettify(input) {
  return input.replace(/\W/g, '');
}

// when a file is added to fileupload, reflect that in the DOM, and add the data
// to the pendingUpload[] list
function onAdd(e, data) {
  if ($('#icon' + prettify(data.files[0].name)).length !== 0) {
    alert(data.files[0].name + " is already selected for upload." + 
      " If this was intentional and these are in fact two different images," +
      " please rename one of them.");
    $( "#processButton" ).button({
      disabled: false
    });
    return;
  }

  console.log("Adding image for upload...");
  successesNeeded += 1;
  pendingUpload.push(data);

  data.context = $('<div class="uploadEntry"/>').appendTo('#selectedImages');

  var img = $('<img class="file-icon" id="icon' + prettify(data.files[0].name) +
    '" src="' + pendingIcon + '"/>');
  var node = $('<div/>')
    .append(img)
    .append($('<span/>').text(data.files[0].name));

  node.appendTo(data.context);
  data.node = node;
}

function onSubmit(e, data) {
  console.log(data.files[0].name + " submitted...");
}

// when a file is successfully uploaded, reflect that in the DOM. if all files
// are successful, clear the pendingUpload[] list and return without continuing;
// otherwise, continue ingesting with the next batch of files
function onDone(e, data) {
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
  //ingest(successesHad + failedFiles.length);
}

function onFail(e, data) {
  for (var i = 0; i < data.files.length; i++) {
    console.log(data.files[i].name + " failed due to " + 
      data.errorThrown + "...");
    $('#icon' + prettify(data.files[i].name)).prop("src", failIcon);
    $('#icon' + prettify(data.files[i].name)).prop
      ("title", "Upload failed! Try re-clicking 'Upload Selected Files'." + 
        " If the problem persists, it may be because your file is too big," +
        " or the filetype is incompatible.");
    failedFiles.push(data.files[i]);
  }

  // If the error was that the file upload was aborted, then the user probably
  // wants to abort the whole upload, not just this batch, so we don't continue
  // ingesting where we left off. Comment out these 3 lines if you are using the
  // tempAbort button for debugging, so as to simulate what would actually
  // happen on real file failures.
}

// for now, changing ingest so it ingests from 0 to the end of the list
function ingest(startIndex) {
  console.log('ingesting');
  var len = pendingUpload.length;
  for (var i = startIndex; i < len; i++) {
    jqXHR = pendingUpload[i].submit();
  }
  /*var filesList = [];

  // add all the files in the batch to filesList and set icons to progressIcon
  for (var i = startIndex; i < startIndex + batchSize 
       && i < successesNeeded; i++) {
    var fileName = pendingUpload[i].files[0].name
    $('#icon' + prettify(fileName)).prop("src", progressIcon);
    filesList.push(pendingUpload[i].files[0]);
  }

  jqXHR = $('#fileupload').fileupload('send', {files: filesList});*/
}

$(document).ready(function() {

  $( "#processButton" ).button({
    disabled: true
  });

  $('#fileupload').fileupload({
    url : url,
    dataType : 'html',
    autoUpload: false,
    limitConcurrentUploads: 20
  });

  jqXHR = $('#fileupload').fileupload('enable')
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
    // first, try re-sending any failed files
    if (failedFiles.length !== 0) {
      var filesList = [];
      // set all failedFiles' icons to progress icon
      for (var i = 0; i < failedFiles.length; i++) {
        var fileName = failedFiles[i].name;
        console.log(i + ': ' + fileName)
        filesList.push(failedFiles[i]);
        $('#icon' + prettify(fileName)).prop("src", progressIcon);
      }

      failedFiles = [];

      // send files
      jqXHR = $('#fileupload').fileupload('send', {files: filesList});
    } else {
      // if there are no files pending upload, do nothing
      if (pendingUpload.length == 0) {
        return;
      }

      // call the ingest function with starting index 0
      ingest(successesHad + failedFiles.length);
    }
  });

  /*
  Listener for the temporary abort button, used while upload failures.
  $('#tempAbort').click(function (e) {
    if (jqXHR.readyState == 1) {
      console.log('Aborting upload!');
      jqXHR.abort();
    }
  })
  */

  $('#clearButton').click(function (e) {
    // if an upload is in progress, abort it
    if (jqXHR.readyState == 1) {
      console.log('Aborting upload');
      jqXHR.abort();
    }

    // reset the pendingUpload list and the DOM list
    pendingUpload = [];
    successesHad = 0;
    successesNeeded = 0;
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

})
