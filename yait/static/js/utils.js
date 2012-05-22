// Toggle extra fieldset in several forms (add/edit issue, add/edit comment)
function toggleExtraFieldset() {
    var $extra = $('#extra-fieldset');
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


// Used in the project configuration page to add a new row in the
// 'roles' table.
function addNewUserInProjectConfig() {
    var $table_body = $('#roles');
    $template = $($table_body.children()[0]);
    var row = $template.clone();
    $(row).removeClass('hidden');
    $table_body.append(row);
}


// Callback on 'select' event in the project configuration form, when
// a user is selected to be granted a role.
function selectNewUserInProjectConfig(selector) {
    var suffix = '_' + selector.options[selector.selectedIndex].value;
    var inputs = $(selector).parent().parent().find('input');
    for (var i = 0; i < inputs.length; i++) {
        var input = inputs[i];
        input.name = 'role' + suffix;
        input.id = input.name;
    }
}


// Used in the project configuration page to remove a previously added
// row in the 'roles' table.
function removeUserInProjectConfig(selector) {
    $(selector).parents('tr').remove();
}


// FIXME: timezone detection does not work well.
// Replace UTC dates with the user's local timezone.
// Should be called after the DOM is ready on any page that may show a date.
function updateDatesWithUserTimezone() {
    var user_timezone = jstz.determine_timezone();
    var offset_str = user_timezone.offset();
    var sign = 1;
    if (offset_str.substring(0, 1) === '-') {
        sign = -1;
    }
    var hours = parseInt(offset_str.substring(1, offset_str.search(':')), 10);
    var minutes = parseInt(offset_str.substring(1 + offset_str.search(':')), 10);
    var offset = 1000 * 60 * sign * (minutes + 60 * hours);  // in ms
    $('.date').each(function () {
        var $elm = $(this);
        var utc = Date.parse($elm.html());
        var local = utc + offset;
        $elm.html(new Date(local).toLocaleString());
    })
}