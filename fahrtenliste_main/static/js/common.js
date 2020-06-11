function getQueryParam(param, defaultValue) {
    var url = Qurl.create();
    var value = url.query(param);
    if (typeof (value) == "undefined") {
        return typeof defaultValue != "undefined" ? defaultValue : null;
    }
    return url.query(param);
}

// ECMAScript 6's String.prototype.startsWith() method, is not yet supported in all browsers, z.B. IE10!
// http://stackoverflow.com/questions/646628/how-to-check-if-a-string-startswith-another-string
function startsWith(string1, string2) {
    if (!isString(string1) || !isString(string2)) {
        return false;
    }
    if (typeof string1 === "undefined" || string1 == null) {
        return false;
    }
    return string1.lastIndexOf(string2, 0) === 0;
}

function isString(f) {
    return typeof (f) === "string" && f !== "NaN";
}
