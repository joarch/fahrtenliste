// https://github.com/ryanburnette/Qurl
var Qurl
;

(function () {
    'use strict';

    var proto;

    Qurl = function () {
        if (!(this instanceof Qurl)) {
            return new Qurl();
        }
    };

    proto = Qurl.prototype;

    proto.query = function (key, value) {
        if (!key) {
            return getSearch();
        }

        if (key && typeof (value) === 'undefined') {
            return getSearch()[key];
        }

        if (key && typeof (value) !== 'undefined') {
            return setSearch(key, value);
        }
    };

    proto.getSearchLength = function () {
        return Object.keys(getSearch()).length
    };

    proto.getSearch = function () {
        return Object.keys(getSearch());
    };

    function getSearch() {
        var string = window.location.search
            , pairs = []
            , obj = {}
        ;

        if (!string) {
            return obj;
        }
        string = string.replace('?', '');

        pairs = string.split('&');
        pairs.forEach(function (p) {
            var pair = decodeURIComponent(p).split('=')
                , key = pair[0]
                , val = pair[1]
            ;

            obj[key] = val;
        });

        return obj;
    }

    function setSearch(key, value) {
        var search = getSearch()
            , string = window.location.search
        ;

        if (value === false) {
            delete search[key];
        } else {
            search[key] = value;
        }

        setSearchString(getSearchString(search));

        return search;
    }

    function setSearchString(string) {
        /** joerg replaceState anstatt pushState, verhindert history back fuer jeden param add
         if ( history.pushState ) {
            history.pushState({}, document.title, string);
         }
         */
        if (history.replaceState) {
            history.replaceState({}, document.title, string);
        }
    }

    function getSearchString(query) {
        var pairs = []
        ;

        Object.keys(query).forEach(function (key) {
            if (typeof query[key] === 'undefined') {
                pairs.push(key);
            } else {
                pairs.push(encodeURIComponent(key) + '=' + encodeURIComponent(query[key] || ''));
            }
        });

        if (pairs.length === 0) {
            return '?';
        } else {
            return '?' + pairs.join('&');
        }
    }

    Qurl.create = Qurl;
}());