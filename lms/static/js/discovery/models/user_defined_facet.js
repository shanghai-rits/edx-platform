;(function (define) {

define([
    'backbone'
    ], function (Backbone) {
    'use strict';

    return Backbone.Model.extend({
        defaults: {
            facet: '',
            term: '',
            course: ''
        }
    });

});


})(define || RequireJS.define);

