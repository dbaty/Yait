// Toggle extra fieldset in several forms (add/edit issue, add/edit comment)
function toggleExtraFieldset() {
    var elm = document.getElementById('extra-fieldset');
    if (elm.className === 'hidden') {
        elm.className = '';
    } else {
        elm.className = 'hidden';
    }
}


// Toggle preview pane (and display rendered text if needed)
function togglePreviewPane(url) {
    var preview_pane = document.getElementById('preview-pane');
    var text_area = document.getElementById('text');
    var text_renderer = document.getElementById('text_renderer');
    var preview_spinner = document.getElementById('preview-spinner');
    if (preview_pane.className === 'hidden') {
        text_area.className = 'hidden';
        preview_spinner.className = '';
        $.getJSON(url,
                  {text: text_area.value, text_renderer: text_renderer.value},
                  function(data) {
                      preview_pane.className = '';
                      preview_pane.innerHTML = data.rendered;
                      preview_spinner.className = 'hidden';
                  }
                 );
    } else {
        text_area.className = '';
        preview_pane.className = 'hidden';
    }
}