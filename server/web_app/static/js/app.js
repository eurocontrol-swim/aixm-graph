

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
        type: "GET",
        url: "/datasets",
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        success : function(response) {
            response.data.forEach(function(dataset) {
                Nav.datasets.push(dataset);
            });
        },
        error: function(response) {
            console.log(response.responseJSON.error);
            showError('Failed to load datasets');
        }
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
