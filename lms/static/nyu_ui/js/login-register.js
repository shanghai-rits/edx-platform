$(function () {

    $(".window-wrap").on("resize", function () {
        let heightWhole = $(document.body).height();
        $(".section-bkg-wrapper").height(heightWhole - $(".global-header").outerHeight());
    });

    // $(".js-form-errors .message-title").text(gettext('An error occurred.'));
    // $("input[type=radio][name=reset_password]").change(function () {
    //     let checked = $("input[type=radio]:checked").val();
    //     $(".field-reset-password:not(#field-" + checked + ")").hide();
    //     $("#field-" + checked).show();
    //     $(".js-form-errors").hide();
    //     $(".form-field .error").removeClass("error");
    // });

    $("i.reset-password-code[name=validate]").click(getSMSCode);
    $("#btn-reset_password").click(function () {
        let checked = $("input[type=radio]:checked").val();
        if (checked == "email") {
            let email = $("input#password-reset-email").val();
            if (!isEmail(email)) {
                $(".email-email>*").addClass("error");
                $(".message-copy").html("<li>" + gettext('The email address you\'ve provided isn\'t formatted correctly.') + "</li>");
                $(".js-form-errors").show();
            } else {
                let form = new FormData();
                form.append("email", email);
                send_ajax(form, function () {
                    $(".js-form-errors").hide();
                    let successTitle = gettext('Check Your Email');
                    let successMessageHtml = interpolate(
                        gettext('{paragraphStart}You entered {boldStart}{email}{boldEnd}. If this email address is associated with your {platform_name} account, we will send a message with password reset instructions to this email address.{paragraphEnd}' + // eslint-disable-line max-len
                            '{paragraphStart}If you do not receive a password reset message, verify that you entered the correct email address, or check your spam folder.{paragraphEnd}' + // eslint-disable-line max-len
                            '{paragraphStart}If you need further assistance, {anchorStart}contact technical support{anchorEnd}.{paragraphEnd}'), { // eslint-disable-line max-len
                            boldStart: '<b>',
                            boldEnd: '</b>',
                            paragraphStart: '<p>',
                            paragraphEnd: '</p>',
                            email: email,
                            platform_name: '',
                            // anchorStart: '<a href="' + 'URL' + '">',
                            anchorStart: '',
                            anchorEnd: '</a>'
                        }
                    );
                    $(".js-password-reset-success .message-title").text(successTitle);
                    $(".js-password-reset-success .message-copy").html(successMessageHtml);
                    $(".js-password-reset-success").show();
                    $("#password-reset").hide();
                })
            }
        } else {
            let phone = $("input#password-reset-phone").val();
            let sms_code = $("input#password-reset-sms_code").val();
            if (!isPhone(phone)) {
                $(".text-phone>*").addClass("error");
                $(".message-copy").html("<li>" + gettext('The phone you\'ve provided isn\'t formatted correctly.') + "</li>");
                $(".js-form-errors").show();
            } else if (!isSmsCode(sms_code)) {
                $(".text-sms_code>*").addClass("error");
                $(".message-copy").html("<li>" + gettext('The sms code you\'ve provided isn\'t formatted correctly.') + "</li>");
                $(".js-form-errors").show();
            } else {
                let form = new FormData();
                form.append("phone", phone);
                form.append("sms_code", sms_code);
                form.append("action", sms_code);
                send_ajax(form, function (data) {
                    if (data.success)
                        location.href = data.value;
                }, function (error) {
                    console.log(JSON.parse(error.responseText));
                    let errors = JSON.parse(error.responseText);
                    if (errors.hasOwnProperty('sms_code')) {
                        $(".text-sms_code>*").addClass("error");
                        $(".message-copy").html("<li>" + gettext(errors.sms_code[0].user_message) + "</li>");
                        $(".js-form-errors").show();
                    }
                    if (errors.hasOwnProperty('value')) {
                        $(".text-phone>*").addClass("error");
                        $(".message-copy").html("<li>" + gettext(errors.value) + "</li>");
                        $(".js-form-errors").show();
                    }
                });
            }
        }
    });
});

window.onload = function () {
    let heightWhole = $(document.body).height();
    $(".section-bkg-wrapper").height(heightWhole - $(".global-header").outerHeight());
};

(function ($, h, c) {
    var a = $([]), e = $.resize = $.extend($.resize, {}), i, k = "setTimeout", j = "resize", d = j
        + "-special-event", b = "delay", f = "throttleWindow";
    e[b] = 350;
    e[f] = true;
    $.event.special[j] = {
        setup: function () {
            if (!e[f] && this[k]) {
                return false
            }
            var l = $(this);
            a = a.add(l);
            $.data(this, d, {
                w: l.width(),
                h: l.height()
            });
            if (a.length === 1) {
                g()
            }
        },
        teardown: function () {
            if (!e[f] && this[k]) {
                return false
            }
            var l = $(this);
            a = a.not(l);
            l.removeData(d);
            if (!a.length) {
                clearTimeout(i)
            }
        },
        add: function (l) {
            if (!e[f] && this[k]) {
                return false
            }
            var n;

            function m(s, o, p) {
                var q = $(this), r = $.data(this, d);
                r.w = o !== c ? o : q.width();
                r.h = p !== c ? p : q.height();
                n.apply(this, arguments)
            }

            if ($.isFunction(l)) {
                n = l;
                return m
            } else {
                n = l.handler;
                l.handler = m
            }
        }
    };

    function g() {
        i = h[k](function () {
            a.each(function () {
                var n = $(this), m = n.width(), l = n.height(), o = $
                    .data(this, d);
                if (m !== o.w || l !== o.h) {
                    n.trigger(j, [o.w = m, o.h = l])
                }
            });
            g()
        }, e[b])
    }
})(jQuery, this);

let getSMSCode = function (event) {

    var phone = $("input#password-reset-phone").val();
    if (!isPhone(phone)) {
        // $(".text-phone label, #password-reset-phone").addClass("error");
        $(".text-phone>*").addClass("error");
        $(".message-copy").html("<li>" + gettext('The phone you\'ve provided isn\'t formatted correctly.') + "</li>");
        $(".js-form-errors").show();
    } else {
        var el = $(event.currentTarget)[0];
        var inactive = $(el).hasClass("inactive");
        var el_val = el.innerText;
        if (inactive) {
            var time = 59;
            var timer = setInterval(function () {
                if (time <= 0) {
                    el.innerText = el_val;
                    el.onclick = this.getSMSCode;
                    clearInterval(timer);
                    $(el).addClass("inactive");
                    $(el).css("background", "#57068c");
                } else {
                    $(el).removeClass("inactive");
                    $(el).css("background", "#57068c82");
                    el.innerText = interpolate(
                        gettext('Try again in {time} seconds'),
                        {time: time}
                    );
                    time--;
                }
            }, 1000);

            var headers = {
                'X-CSRFToken': $.cookie('csrftoken')
            };

            $.ajax({
                url: '/auth/phone',
                type: 'POST',
                data: {phone: phone, action: 'reset_password'},
                headers: headers
            }).done(function () {
                $(".form-field .error").removeClass("error");
                $(".js-form-errors").hide();
            });
        }
    }
};

let interpolate = function (formatString, parameters) {
    return formatString.replace(/{\w+}/g,
        function (parameter) {
            var parameterName = parameter.slice(1, -1);
            return String(parameters[parameterName]);
        });
};

let isPhone = function (phone) {
    let regex_phone = new RegExp("^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$");
    return regex_phone.test(phone);
};

let isEmail = function (email) {
    let regex = new RegExp(
        [
            '(^[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+)*',
            '|^"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\[\\001-\\011\\013\\014\\016-\\177])*"',
            ')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+[A-Z]{2,6}\\.?$)',
            '|\\[(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)(\\.(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)){3}\\]$'
        ].join(''), 'i');
    return regex.test(email);
};

let isSmsCode = function (sms_code) {
    return new RegExp('^[0-9]{6}$').test(sms_code);
};

let send_ajax = function (form, success, fail) {
    var headers = {
        'X-CSRFToken': $.cookie('csrftoken')
    };
    $.ajax({
        url: '/reset_password',
        type: 'POST',
        data: form,
        processData: false,
        contentType: false,
        headers: headers
    }).done(success).fail(fail);

};