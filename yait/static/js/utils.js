// Toggle extra fieldset in several forms (add/edit issue, add/edit comment)
function toggleExtraFieldset() {
    $extra = $('#extra-fieldset');
    if ($extra.hasClass('hidden')) {
        // scroll to the bottom of the form so that the extra fieldset
        // as well as the submit button are visible.
        $extra.removeClass('hidden');
        var $form = $('#extra-fieldset').parent();
        var bottom = $form.offset()['top'] + $form.height();
        $('html, body').animate({scrollTop: bottom}, 750);
    } else {
        $extra.addClass('hidden');
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


// Used in the add issue/comment forms to assign the issue to the
// logged-in user.
function assignIssueTo(user_id) {
    var sel = document.getElementById('assignee');
    for (var i = 0; i < sel.length; i++) {
        if (sel[i].value === user_id) {
            sel.selectedIndex = i;
            return;
        }
    }
}