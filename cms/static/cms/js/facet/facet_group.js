$(function () {
    'use strict';

    $(".group_display").click(function () {

        $(this).parent().parent().find(".group_items").slideToggle("fast");

    });

    $(".group_items").on('click', '.delete_group_item', function () {
        //send delete item ajax
        var headers = {
            'X-CSRFToken': $.cookie('csrftoken')
        };
        var group = $(this).parent().parent().parent().find("input[name='group']").val();
        var lang = $(this).parent().find(".item_languages").val();
        var _this = $(this);
        $.ajax({
            url: '/api/v1/group',
            type: 'DELETE',
            data: {lang: lang, group: group},
            headers: headers
        }).success(function (data) {
            _this.parent().remove();
        }).error(function () {
            alert(gettext("Error"));
        });

    });

    $(".group_items").on('click', '.add_group_item', function () {
        //send add item ajax
        var headers = {
            'X-CSRFToken': $.cookie('csrftoken')
        };
        var group = $(this).parent().parent().parent().find("input[name='group']").val();
        var lang = $(this).parent().find(".item_languages").val();
        var content = $(this).parent().find(".group_item_add").val();
        var _this = $(this);
        $.ajax({
            url: '/api/v1/group',
            type: 'POST',
            data: {lang: lang, group: group, content: content},
            headers: headers
        }).success(function (data) {
            //success callback
            var selectEL = _this.parent().find(".item_languages");
            selectEL.prop("disabled", true);
            var inputEL = _this.parent().find("input");
            inputEL.attr("readonly", true);
            inputEL.attr("class", "group_item_display");
            var cancelbtn = _this.parent().find(".cancel_edit");
            cancelbtn.addClass("delete_group_item");
            cancelbtn.removeClass("cancel_edit");
            _this.remove();
        }).error(function (error) {
            if (error['responseText']) {
                alert(gettext(JSON.parse(error['responseText']).non_field_errors[0]));
            } else {
                alert(gettext("Error"));
            }

        });

    });

    $(".add_line").click(function () {
        var hidden_item = $(this).parent().parent().find(".hidden_item");
        var clone = hidden_item.clone();
        clone.find(".item_languages").prop("disabled", false);
        clone.removeClass("hidden_item");
        $(this).parent().before(clone.prop("outerHTML"));
    });

    $(".group_items").on('click', '.cancel_edit', function () {
        $(this).parent().remove();
    });

});