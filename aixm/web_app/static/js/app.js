//+ function($) {
//    'use strict';
//
//    // UPLOAD CLASS DEFINITION
//    // ======================
//
//    var dropZone = document.getElementById('drop-zone');
//    var uploadForm = document.getElementById('js-upload-form');
//
//    var startUpload = function(files) {
//        console.log(files)
//    }
//
//    uploadForm.addEventListener('submit', function(e) {
//        var uploadFiles = document.getElementById('js-upload-files').files;
//        e.preventDefault()
//
//        startUpload(uploadFiles)
//    })
//
//    dropZone.ondrop = function(e) {
//        e.preventDefault();
//        this.className = 'upload-drop-zone';
//
//        startUpload(e.dataTransfer.files)
//    }
//
//    dropZone.ondragover = function() {
//        this.className = 'upload-drop-zone drop';
//        return false;
//    }
//
//    dropZone.ondragleave = function() {
//        this.className = 'upload-drop-zone';
//        return false;
//    }
//
//}(jQuery);

$(document).ready(function(){
    $.ajax({
        type: "POST",
        url: "/load_aixm",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({filepath: "/media/alex/Data/dev/work/eurocontrol/aixm/samples/EA_AIP_DS_FULL_20170701.xml"}),
//        data: JSON.stringify({filepath: "/media/alex/Data/dev/work/eurocontrol/aixm/samples/BD_2019-01-03_26fe8f56-0c48-4047-ada0-4e1bd91ed4cf.xml"}),
        success : function(result) {
            result.stats.forEach(function(data) {
                featuresList.add(data);
            });
        }
    });
});
