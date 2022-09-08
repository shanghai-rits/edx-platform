(function(define) {
    define([
        'underscore',
        'backbone',
        'js/discovery/models/course_card',
        'js/discovery/models/facet_option'
    ], function(_, Backbone, CourseCard, FacetOption) {
        'use strict';

        return Backbone.Model.extend({
            url: '/search/course_discovery/',
            jqhxr: null,

            defaults: {
                totalCount: 0,
                latestCount: 0,
                terms: {},
                facet_records: []
            },

            initialize: function() {
                this.courseCards = new Backbone.Collection([], {model: CourseCard});
                this.facetOptions = new Backbone.Collection([], {model: FacetOption});
            },

            parse: function(response) {
                var results = response.results || [];
                var selecting = 0;
                var selected = [];
                var courses = [];
                var facets = {};
                var facet_records = this.get('facet_records');
                _(this.get('terms')).each(function(term, facet) {
                    if (facet != "search_query") {
                        var temp = [];
                        facet_records.forEach(function (j) {
                            if (j.get("facet") == facet && j.get("term") == term) {
                                    temp.push(j.get("course"));
                            }
                        })
                        selected = selecting == 0 ? temp :  _.intersection(selected, temp);
                        selecting ++;
                    }
                })

                results.forEach(function (i) {
                if (selecting > 0 && selected.indexOf(i['data']['course']) == -1) {
                    response.total--;
                } else {
                        courses.push(i);
                        facet_records.forEach(function (j) {
                            if (i['data']['course'] == j.get("course")) {
                                i['data'][j.get("facet")] = j.get("term");
                                if (facets[j.get("facet")]) {
                                    if (facets[j.get("facet")]["terms"][j.get("term")]) {
                                        facets[j.get("facet")]["terms"][j.get("term")]++;
                                        facets[j.get("facet")]["total"]++;
                                    } else {
                                        facets[j.get("facet")]["terms"][j.get("term")] = 1;
                                        facets[j.get("facet")]["total"]++;
                                    }
                                } else {
                                    facets[j.get("facet")] = {total: 0, terms: {}, other: 0};
                                    facets[j.get("facet")]["terms"][j.get("term")] = 1;
                                    facets[j.get("facet")]["total"]++;
                                }
                            }
                        })
                }
                })
                this.courseCards.add(_.pluck(courses, 'data'));

                this.set({
                    totalCount: response.total,
                    latestCount: courses.length
                });

                var options = this.facetOptions;
                _(facets).each(function(obj, key) {
                    _(obj.terms).each(function(count, term) {
                        options.add({
                            facet: key,
                            term: term,
                            count: count
                        }, {merge: true});
                    });
                });
            },

            reset: function() {
                this.set({
                    totalCount: 0,
                    latestCount: 0,
                    terms:{}
                });
                this.courseCards.reset();
                this.facetOptions.reset();
            },

            latest: function() {
                return this.courseCards.last(this.get('latestCount'));
            }

        });
    });
}(define || RequireJS.define));
