import '../css/admin.css';

function toggle_link_type($el) {
    var $container = $el.closest('.cta-block-form'),
        prefix = $container.data('prefix'),
        $link_type = $('input[name="'+ prefix + '-link_type"]:checked'),
        link_syntax = 'li[class^="cta-block-link_"]:not(.cta-block-link_type)',
        link_choice = $link_type.val();

    if(link_choice == 'none') {
        $(link_syntax, $container).hide();
    }
    else {
        $(link_syntax, $container).hide();
        $('li[class^="cta-block-link_' + link_choice + '"]', $container).show();
        if(link_choice != 'sms') {
            $('.cta-block-link_label', $container).show();
        }

    }
}

$(document).ready(function() {
    $('.cta-block-link_type input').each(function( index ) {
        toggle_link_type($(this));
    });
    $(document).on('change', '.cta-block-link_type input', function() {
        toggle_link_type($(this));
    });
    $("button.confirm-delete").click(function(e){
        if (confirm("Are you sure you want to delete this message?")){
            return true;
        }
        return false;
    });
})
