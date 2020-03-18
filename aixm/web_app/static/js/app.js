
var config = null;

$(document).ready(function(){

    $.ajax({
        url: '/load-config',
        type: 'GET',
        contentType: false,
        processData: false,
        success: function(response){
            config = response;
        },
    });
    sidenav.init();
});
