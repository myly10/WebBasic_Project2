$(document).ready(function() {
    $("#nav-ask").click(function () {
        $(".new-question-wrapper").css("display", "block");
    });

    $("#new-question-window-title-close").click(function () {
        $(".new-question-wrapper").css("display", "none");
    });


    $("#new-question-submit").click(function () {
        $.post("/question/new", {title: $("#new-question-title").val(), content: $("#new-question-content").val()})
            .done(function (data) {
                window.location.href = "/question/" + data;
            })
            .fail(function () {
                alert('Invalid input');
            });
    });

    $(".nav-form button").click(function () {
            if ($('.nav-form input[type=text]').val()=='') return false;
        }
    );
});