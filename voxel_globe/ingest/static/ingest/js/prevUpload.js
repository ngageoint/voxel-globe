
var pendingUpload = [];
var pendingIcon = "{% static 'ingest/icons/' %}" + "upload_pending.png";
var successIcon = "{% static 'ingest/icons/' %}" + "upload_success.png";
var failIcon = "{% static 'ingest/icons/' %}" + "upload_fail.png";
var url = '{% url "ingest:uploadEndpoint" %}'
            
$('#fileupload').fileupload({ 
  url : url,
  dataType : 'html', 
  autoUpload: false });
$('#fileupload').fileupload('enable').on('fileuploadadd', function (e, data) {
      console.log("Adding image for upload...");
      data.id = pendingUpload.length;
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
  }).on('fileuploadfail', function(e, data) {
      console.log(data + " failed...");
      $('#icon' + data.id).prop("src", failIcon);    
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
  pendingUpload = [];
  $('#selectedImages').html("");
});

$('#processButton').click(function (e) {
  document.forms['ingestfolder'].submit()
  //AEN: Yeah, I don't know your jquery magic
});
