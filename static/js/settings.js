$().ready(function () {
    $(".update-password-button").click(function(){
        var pwd = $('.setting-password-wrapper').find('input').val();

        if (!pwd){
            $('.update-password-status').stop().text('密码不得为空').css( "opacity", 1 ).fadeIn( 0 ).fadeOut( 2000 );
            return false;
        }else if (pwd.length < 6 || pwd.length > 16){
            $('.update-password-status').stop().text('密码长度为6～16字符').css( "opacity", 1 ).fadeIn( 0 ).fadeOut( 2000 );
            return false;
        }else if (/^[0-9]*$/.test(pwd)){
            $('.update-password-status').stop().text('密码不得为纯数字').css( "opacity", 1 ).fadeIn( 0 ).fadeOut( 2000 );
            return false;
        }

        $.post('/settings',{password: pwd})
            .done(function (data) {
                if (data=='ok') $('.update-password-status').stop().text('Done').css( "opacity", 1 ).fadeIn( 0 ).fadeOut( 2000 );
            })
            .fail(function(){
                $('.update-password-status').stop().text('Error').css( "opacity", 1 ).fadeIn( 0 ).fadeOut( 2000 );
            });
    });

    $(".update-motto-button").click(function(){
        $.post('/settings',{motto: $('.setting-motto-wrapper').find('input').val()})
            .done(function (data) {
                if (data=='ok') $('.update-motto-status').stop().css( "opacity", 1 ).fadeIn( 0 ).fadeOut( 2000 );
            })
            .fail(function(){
                $('.update-motto-status').stop().text('Error').css( "opacity", 1 ).fadeIn( 0 ).fadeOut( 2000 );
            });
    });

    $('.update-avatar-button').click(function () {
        var files = $('.setting-avatar-wrapper input')[0].files;
        if (files.length != 0) {
            var fd = new FormData();
            fd.append('file', files[0]);
            $.ajax({
                url: '/upload/avatar',
                type: 'POST',
                data: fd,
                cache: false,
                processData: false,
                contentType: false,
                success: function (data) {
                    $('.avatar-preview').attr("src", '/static/img/avatar/' + data);
                    $('.update-avatar-status').stop().text('Done').css("opacity", 1).fadeIn(0).fadeOut(2000);
                }
            }).fail(function () {
                $('.update-avatar-status').stop().text('Error').css("opacity", 1).fadeIn(0).fadeOut(2000);
            });
        }
    })
});