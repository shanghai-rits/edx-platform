(function(define, undefined) {
    'use strict';
    define([
        'gettext',
        'jquery',
        'underscore',
        'backbone',
        'js/views/fields',
        'text!templates/fields/field_text_account.underscore',
        'text!templates/fields/field_readonly_account.underscore',
        'text!templates/fields/field_link_account.underscore',
        'text!templates/fields/field_dropdown_account.underscore',
        'text!templates/fields/field_phone_account.underscore',
        'text!templates/fields/field_social_link_account.underscore',
        'text!templates/fields/field_order_history.underscore',
        'edx-ui-toolkit/js/utils/string-utils',
        'edx-ui-toolkit/js/utils/html-utils'
    ], function(
        gettext, $, _, Backbone,
        FieldViews,
        field_text_account_template,
        field_readonly_account_template,
        field_link_account_template,
        field_dropdown_account_template,
        field_phone_account_template,
        field_social_link_template,
        field_order_history_template,
        StringUtils,
        HtmlUtils
    ) {
        var timer_sms = null;
        var AccountSettingsFieldViews = {
            ReadonlyFieldView: FieldViews.ReadonlyFieldView.extend({
                fieldTemplate: field_readonly_account_template
            }),
            TextFieldView: FieldViews.TextFieldView.extend({
                fieldTemplate: field_text_account_template
            }),
            DropdownFieldView: FieldViews.DropdownFieldView.extend({
                fieldTemplate: field_dropdown_account_template
            }),
            EmailFieldView: FieldViews.TextFieldView.extend({
                fieldTemplate: field_text_account_template,
                successMessage: function() {
                    return HtmlUtils.joinHtml(
                        this.indicators.success,
                        StringUtils.interpolate(
                            gettext('We\'ve sent a confirmation message to {new_email_address}. Click the link in the message to update your email address.'),  // eslint-disable-line max-len
                            {new_email_address: this.fieldValue()}
                        )
                    );
                }
            }),
            LanguagePreferenceFieldView: FieldViews.DropdownFieldView.extend({
                fieldTemplate: field_dropdown_account_template,

                initialize: function(options) {
                    this._super(options);   // eslint-disable-line no-underscore-dangle
                    this.listenTo(this.model, 'revertValue', this.revertValue);
                },

                revertValue: function(event) {
                    var attributes = {},
                        oldPrefLang = $(event.target).data('old-lang-code');

                    if (oldPrefLang) {
                        attributes['pref-lang'] = oldPrefLang;
                        this.saveAttributes(attributes);
                    }
                },

                saveSucceeded: function() {
                    var data = {
                        language: this.modelValue(),
                        next: window.location.href
                    };

                    var view = this;
                    $.ajax({
                        type: 'POST',
                        url: '/i18n/setlang/',
                        data: data,
                        dataType: 'html',
                        success: function() {
                            view.showSuccessMessage();
                        },
                        error: function() {
                            view.showNotificationMessage(
                                HtmlUtils.joinHtml(
                                    view.indicators.error,
                                    gettext('You must sign out and sign back in before your language changes take effect.')  // eslint-disable-line max-len
                                )
                            );
                        }
                    });
                }

            }),
            TimeZoneFieldView: FieldViews.DropdownFieldView.extend({
                fieldTemplate: field_dropdown_account_template,

                initialize: function(options) {
                    this.options = _.extend({}, options);
                    _.bindAll(this, 'listenToCountryView', 'updateCountrySubheader', 'replaceOrAddGroupOption');
                    this._super(options);  // eslint-disable-line no-underscore-dangle
                },

                listenToCountryView: function(view) {
                    this.listenTo(view.model, 'change:country', this.updateCountrySubheader);
                },

                updateCountrySubheader: function(user) {
                    var view = this;
                    $.ajax({
                        type: 'GET',
                        url: '/api/user/v1/preferences/time_zones/',
                        data: {country_code: user.attributes.country},
                        success: function(data) {
                            var countryTimeZones = $.map(data, function(timeZoneInfo) {
                                return [[timeZoneInfo.time_zone, timeZoneInfo.description]];
                            });
                            view.replaceOrAddGroupOption(
                                'Country Time Zones',
                                countryTimeZones
                            );
                            view.render();
                        }
                    });
                },

                updateValueInField: function() {
                    var options;
                    if (this.modelValue()) {
                        options = [[this.modelValue(), this.displayValue(this.modelValue())]];
                        this.replaceOrAddGroupOption(
                            'Currently Selected Time Zone',
                            options
                        );
                    }
                    this._super(); // eslint-disable-line no-underscore-dangle
                },

                replaceOrAddGroupOption: function(title, options) {
                    var groupOption = {
                        groupTitle: gettext(title),
                        selectOptions: options
                    };

                    var index = _.findIndex(this.options.groupOptions, function(group) {
                        return group.groupTitle === gettext(title);
                    });
                    if (index >= 0) {
                        this.options.groupOptions[index] = groupOption;
                    } else {
                        this.options.groupOptions.unshift(groupOption);
                    }
                }

            }),
            PasswordFieldView: FieldViews.LinkFieldView.extend({
                fieldType: 'button',
                fieldTemplate: field_link_account_template,
                events: {
                    'click button': 'linkClicked'
                },
                initialize: function(options) {
                    this.options = _.extend({}, options);
                    this._super(options);
                    _.bindAll(this, 'resetPassword');
                },
                linkClicked: function(event) {
                    event.preventDefault();
                    this.toggleDisableButton(true);
                    this.resetPassword(event);
                },
                resetPassword: function() {
                    var data = {};
                    data[this.options.emailAttribute] = this.model.get(this.options.emailAttribute);

                    var view = this;
                    var reg = new RegExp(/^[0-9]{10,}@default.com$/g);
                    if (reg.test(data.email)) {
                        view.resetEmailMessage();
                    } else {
                        $.ajax({
                            type: 'POST',
                            url: view.options.linkHref,
                            data: data,
                            success: function () {
                                view.showSuccessMessage();
                                view.setMessageTimeout();
                            },
                            error: function (xhr) {
                                view.showErrorMessage(xhr);
                                view.setMessageTimeout();
                                view.toggleDisableButton(false);
                            }
                        });
                    }
                },
                toggleDisableButton: function(disabled) {
                    var button = this.$('#u-field-link-' + this.options.valueAttribute);
                    if (button) {
                        button.prop('disabled', disabled);
                    }
                },
                setMessageTimeout: function() {
                    var view = this;
                    setTimeout(function() {
                        view.showHelpMessage();
                    }, 6000);
                },
                successMessage: function() {
                    return HtmlUtils.joinHtml(
                        this.indicators.success,
                        HtmlUtils.interpolateHtml(
                            gettext('We\'ve sent a message to {email}. Click the link in the message to reset your password. Didn\'t receive the message? Contact {anchorStart}technical support{anchorEnd}.'),  // eslint-disable-line max-len
                            {
                                email: this.model.get(this.options.emailAttribute),
                                anchorStart: HtmlUtils.HTML(
                                    StringUtils.interpolate(
                                        '<a href="{passwordResetSupportUrl}">', {
                                            passwordResetSupportUrl: this.options.passwordResetSupportUrl
                                        }
                                    )
                                ),
                                anchorEnd: HtmlUtils.HTML('</a>')
                            }
                        )
                    );
                },
                resetEmailMessage: function () {
                    var pwd_msg = HtmlUtils.joinHtml(
                        this.indicators.error,
                        gettext('Please bind your email first so that we can provide password modification service for you.')
                    );
                    var email_msg = HtmlUtils.joinHtml(
                        this.indicators.error,
                        gettext('You have not yet bound your email. Please bind your mailbox as soon as possible so that we can provide you with better service.')
                    );
                    HtmlUtils.setHtml(this.$('.u-field-message-help'), pwd_msg);
                    HtmlUtils.setHtml($('.u-field-email .u-field-message-help'), email_msg);
                    $('#field-input-email').val('')
                }
            }),
            LanguageProficienciesFieldView: FieldViews.DropdownFieldView.extend({
                fieldTemplate: field_dropdown_account_template,
                modelValue: function() {
                    var modelValue = this.model.get(this.options.valueAttribute);
                    if (_.isArray(modelValue) && modelValue.length > 0) {
                        return modelValue[0].code;
                    } else {
                        return null;
                    }
                },
                saveValue: function() {
                    var attributes = {},
                        value = '';
                    if (this.persistChanges === true) {
                        value = this.fieldValue() ? [{code: this.fieldValue()}] : [];
                        attributes[this.options.valueAttribute] = value;
                        this.saveAttributes(attributes);
                    }
                }
            }),

            PhoneFieldView: FieldViews.TextFieldView.extend({
                fieldTemplate: field_phone_account_template,
                events: {
                    'click .bind_phone': 'editPhone',
                    'click .verify_btn': 'getSMSCode',
                    'blur .change-phone': 'checkPhone',
                    'click .cancel_btn': 'cancelEdit',
                    'click .save_phone': 'savePhone',
                },
                initialize: function (options) {
                    this.options = _.extend({}, options);
                    this._super(options);
                    _.bindAll(this, 'checkBindPhone');
                    this.checkBindPhone();
                },
                render: function () {
                    HtmlUtils.setHtml(this.$el, HtmlUtils.template(this.fieldTemplate)({}));
                    return this;
                },
                savePhone: function () {
                    var newPhone = $(".change-phone").val();
                    var smsCode = $(".verify_input").val();
                    var headers = {
                        'X-CSRFToken': $.cookie('csrftoken')
                    };

                    $.ajax({
                        url: '/api/v1/phone',
                        type: 'PATCH',
                        data: {phone: newPhone, sms_code: smsCode},
                        headers: headers
                    }).success(function (data) {
                        if (data.phone) {
                            alert(gettext("Change success!"));
                            $(".edit_view").hide();
                            $(".basic_view").show();
                            var fuzzy_phone = data.phone.replace(/^(\d{3})\d*(\d{4})$/, "$1****$2");
                            var default_input = $(".basic_default").find("input");
                            default_input.val(fuzzy_phone);
                            default_input.attr("data-value", data.phone);
                            $(".bind_phone").text(gettext("Change"));
                            $(".u-field-message-phone-notification").text('');
                        } else {
                            $(".u-field-message-phone-notification").text(gettext('Incorrect verification sms code'));

                        }
                    }).fail(function () {
                        $(".u-field-message-phone-notification").text(gettext('Incorrect verification sms code'));
                    });
                },
                cancelEdit: function () {
                    $(".edit_view").hide();
                    $(".basic_view").show();
                    $(".u-field-message-phone-notification").text('');

                },
                editPhone: function () {
                    $(".basic_view").hide();
                    $(".edit_view").show();
                    $(".verify_input").val('');
                },
                checkPhone: function () {
                    var newPhone = $(".change-phone").val();
                    var regex_phone = new RegExp("^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$");
                    var isPhone = regex_phone.test(newPhone);
                    if (isPhone) {
                        var headers = {
                            'X-CSRFToken': $.cookie('csrftoken')
                        };

                        $.ajax({
                            url: '/api/v1/phone',
                            type: 'POST',
                            data: {phone: newPhone},
                            headers: headers
                        }).success(function (data) {
                            if (data.exist) {
                                $(".u-field-message-phone-notification").text(gettext('Exist phone number'));
                                $(".verify_btn").attr("disabled", true);
                                $(".save_phone").attr("disabled", true);
                            } else {
                                $(".u-field-message-phone-notification").text('');
                                $(".save_phone").attr("disabled", false);
                                if ($(".verify_btn").hasClass("inactive")) {
                                    $(".verify_btn").attr("disabled", false);
                                }
                            }
                        });
                    } else {
                        $(".u-field-message-phone-notification").text(gettext('Phone is empty or wrong phone number'));
                        $(".verify_btn").attr("disabled", true);
                        $(".save_phone").attr("disabled", true);

                    }
                },
                checkBindPhone: function () {
                    $.ajax({
                        type: 'GET',
                        url: '/api/v1/phone',
                        success: function (data) {
                            if (data.phone != null) {
                                var fuzzy_phone = data.phone.replace(/^(\d{3})\d*(\d{4})$/, "$1****$2");
                                var default_input = $(".basic_default").find("input");
                                default_input.val(fuzzy_phone);
                                default_input.attr("data-value", data.phone);
                            } else {
                                $(".bind_phone").text(gettext("Bind"));
                            }
                        },
                        error: function (xhr) {
                            view.showErrorMessage(xhr);
                        }
                    });
                },
                getSMSCode: function (event) {
                    var el = $(event.currentTarget)[0];
                    var inactive = $(el).hasClass("inactive");
                    var el_val = el.innerText;
                    if (inactive) {
                        var time = 59;
                        timer_sms = setInterval(function () {
                            if (time <= 0) {
                                el.innerText = el_val;
                                el.onclick = this.getSMSCode;
                                clearInterval(timer_sms);
                                $(".verify_btn").removeClass("active");
                                $(".verify_btn").addClass("inactive");
                                var newPhone = $(".change-phone").val();
                                var regex_phone = new RegExp("^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$");
                                var isPhone = regex_phone.test(newPhone);
                                if (isPhone) {
                                    var headers = {
                                        'X-CSRFToken': $.cookie('csrftoken')
                                    };

                                    $.ajax({
                                        url: '/api/v1/phone',
                                        type: 'POST',
                                        data: {phone: newPhone},
                                        headers: headers
                                    }).success(function (data) {
                                        if (data.exist) {
                                            $(".u-field-message-phone-notification").text(gettext('Exist phone number'));
                                            $(".verify_btn").attr("disabled", true);
                                            $(".save_phone").attr("disabled", true);
                                        } else {
                                            $(".u-field-message-phone-notification").text('');
                                            $(".save_phone").attr("disabled", false);
                                            if ($(".verify_btn").hasClass("inactive")) {
                                                $(".verify_btn").attr("disabled", false);
                                            }
                                        }
                                    });
                                } else {
                                    $(".u-field-message-phone-notification").text(gettext('Phone is empty or wrong phone number'));
                                    $(".verify_btn").attr("disabled", true);
                                    $(".save_phone").attr("disabled", true);

                                }
                            } else {
                                $(".verify_btn").addClass("active");
                                $(".verify_btn").removeClass("inactive");
                                $(".verify_btn").attr("disabled", true);
                                el.innerText = StringUtils.interpolate(
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
                            data: {phone: $(".item_value input[name='phone']").val(), action: 'modify'},
                            headers: headers
                        });
                    }
                },

            }),

            SocialLinkTextFieldView: FieldViews.TextFieldView.extend({
                render: function() {
                    HtmlUtils.setHtml(this.$el, HtmlUtils.template(field_text_account_template)({
                        id: this.options.valueAttribute + '_' + this.options.platform,
                        title: this.options.title,
                        value: this.modelValue(),
                        message: this.options.helpMessage,
                        placeholder: this.options.placeholder || ''
                    }));
                    this.delegateEvents();
                    return this;
                },

                modelValue: function() {
                    var socialLinks = this.model.get(this.options.valueAttribute);
                    for (var i = 0; i < socialLinks.length; i++) { // eslint-disable-line vars-on-top
                        if (socialLinks[i].platform === this.options.platform) {
                            return socialLinks[i].social_link;
                        }
                    }
                    return null;
                },
                saveValue: function() {
                    var attributes, value;
                    if (this.persistChanges === true) {
                        attributes = {};
                        value = this.fieldValue() != null ? [{platform: this.options.platform,
                            social_link: this.fieldValue()}] : [];
                        attributes[this.options.valueAttribute] = value;
                        this.saveAttributes(attributes);
                    }
                }
            }),
            ExtendedFieldTextFieldView: FieldViews.TextFieldView.extend({
                render: function() {
                    HtmlUtils.setHtml(this.$el, HtmlUtils.template(field_text_account_template)({
                        id: this.options.valueAttribute + '_' + this.options.field_name,
                        title: this.options.title,
                        value: this.modelValue(),
                        message: this.options.helpMessage,
                        placeholder: this.options.placeholder || ''
                    }));
                    this.delegateEvents();
                    return this;
                },

                modelValue: function() {
                    var extendedProfileFields = this.model.get(this.options.valueAttribute);
                    for (var i = 0; i < extendedProfileFields.length; i++) { // eslint-disable-line vars-on-top
                        if (extendedProfileFields[i].field_name === this.options.fieldName) {
                            return extendedProfileFields[i].field_value;
                        }
                    }
                    return null;
                },
                saveValue: function() {
                    var attributes, value;
                    if (this.persistChanges === true) {
                        attributes = {};
                        value = this.fieldValue() != null ? [{field_name: this.options.fieldName,
                            field_value: this.fieldValue()}] : [];
                        attributes[this.options.valueAttribute] = value;
                        this.saveAttributes(attributes);
                    }
                }
            }),
            ExtendedFieldListFieldView: FieldViews.DropdownFieldView.extend({
                fieldTemplate: field_dropdown_account_template,
                modelValue: function() {
                    var extendedProfileFields = this.model.get(this.options.valueAttribute);
                    for (var i = 0; i < extendedProfileFields.length; i++) { // eslint-disable-line vars-on-top
                        if (extendedProfileFields[i].field_name === this.options.fieldName) {
                            return extendedProfileFields[i].field_value;
                        }
                    }
                    return null;
                },
                saveValue: function() {
                    var attributes = {},
                        value;
                    if (this.persistChanges === true) {
                        value = this.fieldValue() ? [{field_name: this.options.fieldName,
                            field_value: this.fieldValue()}] : [];
                        attributes[this.options.valueAttribute] = value;
                        this.saveAttributes(attributes);
                    }
                }
            }),
            AuthFieldView: FieldViews.LinkFieldView.extend({
                fieldTemplate: field_social_link_template,
                className: function() {
                    return 'u-field u-field-social u-field-' + this.options.valueAttribute;
                },
                initialize: function(options) {
                    this.options = _.extend({}, options);
                    this._super(options);
                    _.bindAll(this, 'redirect_to', 'disconnect', 'successMessage', 'inProgressMessage');
                },
                render: function() {
                    var linkTitle = '',
                        linkClass = '',
                        subTitle = '',
                        screenReaderTitle = StringUtils.interpolate(
                            gettext('Link your {accountName} account'),
                            {accountName: this.options.title}
                        );
                    if (this.options.connected) {
                        linkTitle = gettext('Change');
                        linkClass = 'social-field-linked';
                        subTitle = StringUtils.interpolate(
                            gettext('You can use your {accountName} account to sign in to your {platformName} account.'),  // eslint-disable-line max-len
                            {accountName: this.options.title, platformName: this.options.platformName}
                        );
                        screenReaderTitle = StringUtils.interpolate(
                            gettext('Unlink your {accountName} account'),
                            {accountName: this.options.title}
                        );
                    } else if (this.options.acceptsLogins) {
                        linkTitle = gettext('Link');
                        linkClass = 'social-field-unlinked';
                        subTitle = StringUtils.interpolate(
                            gettext('Link your {accountName} account to your {platformName} account and use {accountName} to sign in to {platformName}.'),  // eslint-disable-line max-len
                            {accountName: this.options.title, platformName: this.options.platformName}
                        );
                    }

                    HtmlUtils.setHtml(this.$el, HtmlUtils.template(this.fieldTemplate)({
                        id: this.options.valueAttribute,
                        title: this.options.title,
                        screenReaderTitle: screenReaderTitle,
                        linkTitle: linkTitle,
                        subTitle: subTitle,
                        linkClass: linkClass,
                        linkHref: '#',
                        message: this.helpMessage
                    }));
                    this.delegateEvents();
                    return this;
                },
                linkClicked: function(event) {
                    event.preventDefault();

                    

                    if (this.options.connected) {
                        this.disconnect();
                    } else {
                        this.showInProgressMessage();
                        // Direct the user to the providers site to start the authentication process.
                        // See python-social-auth docs for more information.
                        this.redirect_to(this.options.connectUrl);
                    }
                },
                redirect_to: function(url) {
                    window.location.href = url;
                },
                disconnect: function() {
                    var cfm = confirm(gettext("Make sure to change the linked account?"));
                    if (cfm == true) {
                        var data = {};
                        this.showInProgressMessage();
                        // Disconnects the provider from the user's edX account.
                        // See python-social-auth docs for more information.
                        var view = this;
                        this.redirect_to(this.options.connectUrl);
                    }
                },
                inProgressMessage: function() {
                    return HtmlUtils.joinHtml(this.indicators.inProgress, (
                        this.options.connected ? gettext('Relink') : gettext('Linking')
                    ));
                },
                successMessage: function() {
                    return HtmlUtils.joinHtml(this.indicators.success, gettext('Successfully Relink.'));
                }
            }),

            OrderHistoryFieldView: FieldViews.ReadonlyFieldView.extend({
                fieldType: 'orderHistory',
                fieldTemplate: field_order_history_template,

                initialize: function(options) {
                    this.options = options;
                    this._super(options);
                    this.template = HtmlUtils.template(this.fieldTemplate);
                },

                render: function() {
                    HtmlUtils.setHtml(this.$el, this.template({
                        totalPrice: this.options.totalPrice,
                        orderId: this.options.orderId,
                        orderDate: this.options.orderDate,
                        receiptUrl: this.options.receiptUrl,
                        valueAttribute: this.options.valueAttribute,
                        lines: this.options.lines
                    }));
                    this.delegateEvents();
                    return this;
                }
            })
        };

        return AccountSettingsFieldViews;
    });
}).call(this, define || RequireJS.define);
