// Toggle extra fieldset in several forms (add/edit issue, add/edit comment)
function toggleExtraFieldset() {
    var elm = document.getElementById('extraFieldset');
    if (elm.className == 'hidden') {
        elm.className = '';
    } else {
        elm.className = 'hidden';
    }
}


// Toggle preview pane (and display rendered text if needed)
function togglePreviewPane(url) {
    var preview_pane = document.getElementById('previewPane');
    var text_area = document.getElementById('text');
    if (preview_pane.className == 'hidden') {
        text_area.className = 'hidden';
        preview_pane.className = '';
        $.getJSON(url,
                  {text: text_area.value},
                  function(data) {
                      preview_pane.innerHTML = data.rendered;
                  }
                 );
    } else {
        text_area.className = '';
        preview_pane.className = 'hidden';
    }
}