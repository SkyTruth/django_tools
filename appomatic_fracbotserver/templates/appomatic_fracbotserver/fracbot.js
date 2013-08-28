// ==UserScript==
// @name       FracBot
// @namespace  http://skytruth.org/
// @version    0.1
// @description  Scrapes FracFocus pdf:s for you :)
// @match      http://www.fracfocusdata.org/*
// @copyright  2012+, egil@skytruth.org
// ==/UserScript==

// http://garysieling.com/blog/parsing-pdfs-at-scale-with-node-js-pdf-js-and-lunr-js

var fracbotUrl = "{{site_url}}/fracbot";
var siteinfoUrl = "{{site_url}}/siteinfo";
var downloadAllTimeout = 2000; // seconds between each download...

function zipToDict(keys, values) {
    var res = {};
    values.map(function (idx, value) {
        res[keys[idx]] = value;
    })
    return res;
}

function downloadRow(row, cb) {
    var rowspec = /.*__doPostBack\('(.*)','(.*)'\).*/.exec($(row).find("td input")[0].onclick.toString());
    theForm.__EVENTTARGET.value = rowspec[1];
    theForm.__EVENTARGUMENT.value = rowspec[2];

    $(row).find(".update").html('Downloading..');
    $.ajax({
        url: theForm.action,
        type: "POST",
        data:$(theForm).serialize(),
        beforeSend: function(xhr) {
            xhr.overrideMimeType("text/plain; charset=x-user-defined");
        },
        success: function(data, textStatus, jqXHR) {
            $(row).find(".update").html('Uploading...');
            // No idea why this mangling is necessary, but it is :S      
            var res = "";
            for (x=0; x < data.length; x++) res += String.fromCharCode(data.charCodeAt(x) & 0xff);
            data = res;
            globalData = data;
            globalTextStatus = textStatus;
            globalJqXHR = jqXHR;
        
            $.ajax({
                url: fracbotUrl + "/parse-pdf",
                type: "POST",
                data: {pdf: btoa(data), 'row': JSON.stringify(parseRow(row))},
                success: function (data, textStatus, jqXHR) {
                    globalParsedData = data;
                    updateRow(row, data)
                    if (cb) cb(data);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $(row).find(".update").html('Failed :(');
                    if (cb) cb();
                },
                dataType: "json"
            });
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $(row).find(".update").html('Failed :(');
            if (cb) cb();
        },
    });
}

function downloadRows() {
    var rows = $("#MainContent_GridView1 tr:not(.PagerStyle):has(td.isnew)");
    var idx = -1;
    var next = function() {
        idx++;
        if (idx < rows.length) {
            downloadRow(rows[idx], function () { setTimeout(next, downloadAllTimeout); });
        }
    }
    next();
}

function getColumnHeadings() {
    return $("#MainContent_GridView1 tr:not(.PagerStyle) th").map(function (idx, col) { return $(col).text().trim(); });
}

function parseRow(row) {
    return zipToDict(getColumnHeadings(), $(row).find("td").map(function (idx, col) { return $(col).text().trim(); }))
}

function parseRows() {
    var res = [];
    $("#MainContent_GridView1 tr:not(.PagerStyle):not(:has(th))").map(function (idx, row) {
        res.push(parseRow(row));
    });
    return res;
}

function updateRow(row, rowdata) {
    var columnHeadings = getColumnHeadings();
    row = zipToDict(columnHeadings, $(row).find("td"));
    if (!rowdata.pdf_content) {
        var btn = $("<a href='javascript:void(0);'>Update</a>");
        btn.click(function (ev) {
            downloadRow($(ev.target).parent().parent());
        });
        $(row['Update all']).addClass('isnew');
        $(row['Update all']).html(btn);
    } else {
        $(row['Update all']).removeClass('isnew');
        $(row['Update all']).html('');
    }
    if (rowdata.well_guuid && $(row['API No.']).find("a").length == 0) $(row['API No.']).wrapInner("<a href='" + siteinfoUrl + "/" + rowdata.well_guuid + "'>");
    if (rowdata.site_guuid && $(row['WellName']).find("a").length == 0) $(row['WellName']).wrapInner("<a href='" + siteinfoUrl + "/" + rowdata.site_guuid + "'>");
    if (rowdata.event_guuid && $(row['Job Start Dt']).find("a").length == 0) $(row['Job Start Dt']).wrapInner("<a href='" + siteinfoUrl + "/" + rowdata.event_guuid + "'>");
    if (rowdata.operator_guuid && $(row['Operator']).find("a").length == 0) $(row['Operator']).wrapInner("<a href='" + siteinfoUrl + "/" + rowdata.operator_guuid + "'>");
}

function updatePage () {
    $("#MainContent_GridView1 tr.PagerStyle td").attr("colspan", 12);
    var btn = $("<a href='javascript:void(0);'>Update all</a>");
    btn.click(downloadRows);
    var header = $("<th></th>");
    header.prepend(btn);
    $("#MainContent_GridView1 tr:not(.PagerStyle):has(th)").prepend(header);
    $("#MainContent_GridView1 tr:not(.PagerStyle):not(:has(th))").prepend("<td class='update'></td>")
   
    $.post(fracbotUrl + "/check-records", {records: JSON.stringify(parseRows())}, function (data, textStatus, jqXHR) {
        $("#MainContent_GridView1 tr:not(.PagerStyle):not(:has(th))").map(function (idx, row) {
            updateRow(row, data[idx]);
        });
    }, "json");
    
  //downloadRow($("tr td:contains('42-493-32571-00-00')").parent());
  // $("#MainContent_cboStateList")[0].value = 42; // Texas 
}

$(document).ready(function () {
    var rpm = Sys.WebForms.PageRequestManager.getInstance();
    rpm.add_endRequest(updatePage);
    updatePage();
});
