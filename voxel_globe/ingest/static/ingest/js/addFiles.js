

/*


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
        

*/