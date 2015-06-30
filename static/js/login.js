(function() {
    var signup = document.getElementById('form-signup'),
        signin = document.getElementById('form-signin');

    switchForms();
    checkSignup();
    checkSignin();

    // switch forms
    function switchForms() {
        var label = document.getElementById('form-label');
        label.addEventListener('click', function(e) {
            var signupCls = signup.classList,
                signinCls = signin.classList;
            if (signupCls.contains('hidden')) {
                signupCls.remove('hidden');
                signinCls.add('hidden');
                label.innerHTML = '登陆';
            } else {
                signinCls.remove('hidden');
                signupCls.add('hidden');
                label.innerHTML = '注册';
            }
        }, false);
    }

    // check signup form
    function checkSignup() {
        var nameIpt = signup['username'],
            emailIpt = signup['email'],
            pwdIpt = signup['password'],
            errArea = document.getElementById('signup-error'),
            submitBtn = document.getElementById('signup-submit');

        submitBtn.addEventListener('click', function(e) {
            var err = [];

            var name = nameIpt.value.trim();
            if (!name) {
                err.push('用户名不得为空');
            } else if (name.length < 2 || name.length > 16) {
                err.push('用户名长度为2～16字符');
            }

            var email = emailIpt.value.trim();
            if (!email) {
                err.push('邮箱地址不得为空');
            } else if (!/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(email)) {
                err.push('请输入有效的邮箱地址');
            }

            var pwd = pwdIpt.value;
            if (!pwd) {
                err.push('密码不得为空');
            } else if (pwd.length < 6 || pwd.length > 16) {
                err.push('密码长度为6～16字符');
            } else if (/^[0-9]*$/.test(pwd)) {
                err.push('密码不得为纯数字');
            }

            if (err.length) {
                errArea.innerHTML = err.join('<br>');
            } else {
                $.post($(signup).attr('action'), {username: name, email: email, password: pwd})
                    .done(function(r){
                        if (r!='true') errArea.innerHTML="用户名或密码错误";
                        else window.location.href='/discovery';
                    })
                    .fail(function () {
                        errArea.innerHTML="用户名或邮箱已被注册，或输入数据不合法";
                    });
            }
        }, false);
    }

    // check signin form
    function checkSignin() {
        var emailIpt = signin['email'],
            pwdIpt = signin['password'],
            errArea = document.getElementById('signin-error'),
            submitBtn = document.getElementById('signin-submit');

        submitBtn.addEventListener('click', function(e) {
            var err = [];

            var email = $(emailIpt).val().trim();
            if (!email) {
                err.push('邮箱地址不得为空');
            } else if (!/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(email)) {
                err.push('请输入有效的邮箱地址');
            }

            var pwd = $(pwdIpt).val();
            if (!pwd) {
                err.push('密码不得为空');
            }

            if (err.length) {
                errArea.innerHTML = err.join('<br>');
            } else {
                $.post($(signin).attr('action'), {email: email, password: pwd})
                    .done(function(r){
                        if (r!='true') errArea.innerHTML="用户名或密码错误";
                        else location.reload();
                    })
                    .fail(function () {
                        errArea.innerHTML="用户名或密码错误，或输入数据不合法";
                    });
            }
        }, false);
    }

})();
