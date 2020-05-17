function getQueryParam(param, defaultValue) {
    var url = Qurl.create();
    var value = url.query(param);
    if (typeof (value) == "undefined") {
        return typeof defaultValue != "undefined" ? defaultValue : null;
    }
    return url.query(param);
}