
var config = null;
var Files = {}

function showError(text) {
    html = '<i class="material-icons">warning</i> <span style="margin-left: 10px;">' + text + '</span>';

    M.toast({
        html: html,
        displayLength: 10000,
        classes: 'rounded red lighten-1'
    });
}


function showWarning(text) {
    html = '<i class="material-icons">warning</i> <span style="margin-left: 10px; color: black">' + text + '</span>';

    M.toast({
        html: html,
        displayLength: 10000,
        classes: 'rounded orange lighten-3'
    });
}

function copyToClipboard(str) {
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
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
    Sidenav.init();
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
});

$(document).keydown(function(e){
    if(e.which === 67 && e.ctrlKey){
        var tooltip = $("#node-tooltip")[0];
        if (tooltip) {
            var nodeId = tooltip.getAttribute('data-node-id');
            copyToClipboard(nodeId);
        }
    }
});
