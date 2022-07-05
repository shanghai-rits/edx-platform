(function(define) {
    'use strict';
    define(['jquery', 'backbone'],
        function($, Backbone) {
            return Backbone.Model.extend({
                defaults: {
                    phone: '',
                    action: ''
                },
                ajaxType: '',
                urlRoot: '',

                initialize: function(attributes, options) {
                    this.ajaxType = options.method;
                    this.urlRoot = options.url;
                },

                sync: function(method, model) {
                    var headers = {'X-CSRFToken': $.cookie('csrftoken')},
                        data = {},
                        analytics;

                    $.extend(data, model.attributes, {analytics: analytics});

                    $.ajax({
                        url: model.urlRoot,
                        type: model.ajaxType,
                        data: data,
                        headers: headers,
                        success: function() {
                            window.rudderanalytics.track('edx.bi.smscode.request', data);
                            model.trigger('sync');
                        },
                        error: function(error) {
                            model.trigger('error', error);
                        }
                    });
                    }
            });
        });
}).call(this, define || RequireJS.define);
