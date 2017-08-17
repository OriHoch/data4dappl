$(function() {
    $('.nav-facet .nav-item a span').each(function(i, elt) {
        var $elt = $(elt);
        var txt = $elt.text();
        var tmp = txt.split(" ");
        if (tmp.length > 1 && tmp[tmp.length-1].length > 1 && tmp[tmp.length-1][0] == "(") {
            txt = tmp.slice(0, tmp.length-1).join(" ");
            var mark = (CKAN_LANG=="he") ? " &rlm;" : " &lrm;";
            txt += mark + tmp[tmp.length-1];
            $elt.html(txt);
        }
    });
});
