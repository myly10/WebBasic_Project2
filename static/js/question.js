$(document).ready(function () {
    $("#submit-answer").click(function () {
        $.post(
            $("#publish-form").attr("action"),
            {operation: 'answer', content: $("#answer-content").val()}
        ).done(function (data) {
                $("#answers-wrapper").append(data);
                $("#answer-content").val('');
            }
        ).fail(function () {
                alert('Failed');
            }
        );
        return false;
    });

    $('#answer-image-file').change(function () {
        var files = $('#answer-image-file')[0].files;
        if (files.length != 0) {
            var fd = new FormData();
            fd.append('file', files[0]);
            $.ajax({
                url: '/upload/image',
                type: 'POST',
                data: fd,
                cache: false,
                processData: false,
                contentType: false,
                success: function (data) {
                    var ac = $("#answer-content");
                    ac.val(ac.val() + "<img src='/static/upload/" + data + "'></img>");
                }
            }).fail(function () {
                alert('Failed');
            });
        }
    });

    $("#show-more-wrapper").click(function () {
        $.post($("#publish-form").attr("action"), {operation: 'fetch', start: $('.answer-wrapper').length})
            .done(function (r) {
                var o= $.parseJSON(r);
                if (o.finished==true) $("#show-more-wrapper").remove();
                $("#answers-wrapper").append(o.dat);
            })
            .fail(function () {
                alert('Failed');
            });
    });

    $("#answers-wrapper").click(function (e) {
        var target = $(e.target);
        if (target.is(".comments")) {
            var ansblock = $(target).parents(".answer-wrapper");
            var cblock = $(ansblock).find(".comments-wrapper");
            if ($(cblock).css("display") == "none") {
                $(cblock).css("display", "block");
                $.post(
                    $(ansblock).find("form").attr("action"),
                    {operation: 'fetch'}
                ).done(function (data) {
                        $(cblock).find(".comments-content-wrapper").html(data);
                    }
                ).fail(function () {
                        alert('Failed');
                    }
                );
            }
            else ($(cblock).css("display", "none"));
        }
        else if (target.is(".new-comment-submit")) {
            var ccblock = $(target).parents(".comments-wrapper").find(".comments-content-wrapper");
            var form = $(target).parents("form");
            var new_comment = $(form).find("textarea");
            var ansblock = $(target).parents(".answer-wrapper");
            $.post(
                $(form).attr("action"),
                {operation: 'comment', content: $(new_comment).val()}
            ).done(function (data) {
                    $(ccblock).append(data);
                    var label = $(ansblock).find(".comments");
                    var cn = $(label).data("comments-n") + 1;
                    $(label).data("comments-n", cn);
                    $(label).html("评论(" + cn + ")");
                    $(new_comment).val('');
                }
            ).fail(function () {
                alert('Failed');
            });
            return false;
        }
    });
});