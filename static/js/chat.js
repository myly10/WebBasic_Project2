$().ready(function(){
    $('.new-message-submit').click(function(){
        var msg=$('.new-message-content').val();
        $.post(window.location.pathname, {msg: msg})
            .done(function (data) {
                $('.all-messages').append(data);
                $('.new-message-content').val('');
            })
            .fail(function () {
                alert('Failed');
            });
        return false;
    });
});