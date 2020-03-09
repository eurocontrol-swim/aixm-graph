
function validate() {
    $.ajax({
        type: "POST",
        url: "/load_aixm",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({filename: $("#data-set").attr('data-filename')}),
        success : function(result) {
            result.stats.forEach(function(data) {
                featuresList.add(data);
            });
        }
    });
}

function uploadAIXMFile() {
    var formData = new FormData(),
        fileInputElement = $("#aixm-upload")[0];

    formData.append("file", fileInputElement.files[0]);

    $.ajax({
        url: '/upload',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response){
            console.table(response);
            $("#aixm-upload-button").html('Upload AIXM');
            $("#data-set").html('<strong>Data Set: '+ response.filename +'</strong>')
            $("#data-set").attr('data-filename', response.filename);
        },
    });
    $("#aixm-upload-button").html('Uploading... <i class="fas fa-spinner fa-spin trash">');
}
