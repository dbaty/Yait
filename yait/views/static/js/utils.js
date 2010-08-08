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
    var preview_spinner = document.getElementById('previewSpinner');
    if (preview_pane.className == 'hidden') {
        text_area.className = 'hidden';
        preview_spinner.className = '';
        $.getJSON(url,
                  {text: text_area.value},
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


// Pin the meta information panel, i.e. make it fixed, insensible to
// window scrolling.
function pinMetaPanel() {
    // We want to pin the panel only when needed, i.e. not when it
    // would overlap the footer.
    // FIXME: make sure that this is the correct way under IE.
    if (document.documentElement.clientHeight < document.body.offsetHeight) {
        var panel = document.getElementById('meta');
        var top = panel.offsetTop;
        var left = panel.offsetLeft;
        panel.style.top = top + 'px';
        panel.style.left = left + 'px';
        panel.style.position = 'fixed';
    }
}