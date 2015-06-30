(function() {
    var tabs = [].slice.call(document.querySelectorAll('#myTab .tab'));
    var tabpanes = [].slice.call(document.querySelectorAll('#myTab .tabpane'));

    tabs.forEach(function(tab) {
        tab.addEventListener('click', function(e) {
            var target = this;
            tabs.forEach(function(tab, i) {
                if (target === tab) {
                    tab.classList.add('active');
                    tabpanes[i].classList.add('active');
                } else {
                    tab.classList.remove('active');
                    tabpanes[i].classList.remove('active');
                }
            });
        }, false);
    });
})();

$().ready(function(){
    $(".follow-him").click(function (){
        console.log($(this).data("followed"));
        var followBtn=$(this);
        if ($(followBtn).data("followed").toLowerCase()=="true") {
            $.post(window.location.pathname+'/follow', {operation: 'unfollow'})
                .done(function(){
                    $(followBtn).html("Follow him/her");
                    $(followBtn).data("followed", 'false');
                })
                .error(function () {
                    alert('Failed');
                });
        }
        else{
            $.post(window.location.pathname+'/follow', {operation: 'follow'})
                .done(function() {
                    $(followBtn).html("Stop following");
                    $(followBtn).data("followed", 'true');
                })
                .error(function () {
                    alert('Failed');
                });
        }
    });

    $('.chat-him').click(function(){
        window.location.href=$('.chat-him').data('chat-link');
    });
});