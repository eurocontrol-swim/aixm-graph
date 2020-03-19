
var config = null;

function showError(text) {
    html = '<i class="material-icons">warning</i> <span style="margin-left: 10px;">' + text + '</span>';

    M.toast({
        html: html,
        displayLength: 10000,
        classes: 'rounded red lighten-1'
    });
}

$(document).ready(function(){
    $.ajax({
        url: '/load-config',
        type: 'GET',
        contentType: false,
        processData: false,
        success: function(response){
            config = response.data;
        },
    });
    sidenav.init();
});
