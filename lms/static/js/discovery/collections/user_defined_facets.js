;(function (define) {

define([
    'backbone',
    'js/discovery/models/user_defined_facet'
    ], function (Backbone, UserDefinedFacet) {
    'use strict';

    return Backbone.Collection.extend({
        url: '/facet/',
        model: UserDefinedFacet
    });

});


})(define || RequireJS.define);
