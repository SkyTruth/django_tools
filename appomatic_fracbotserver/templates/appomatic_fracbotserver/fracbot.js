// ==UserScript==
// @name       FracBot
// @namespace  http://skytruth.org/
// @version    0.1
// @description  Scrapes FracFocus pdf:s for you :)
// @match      http://www.fracfocusdata.org/*
// @match      http://fracfocusdata.org/*
// @include    http://www.fracfocusdata.org/*
// @include    http://fracfocusdata.org/*
// @grant      none
// @copyright  2012+, egil@skytruth.org
// ==/UserScript==

// http://garysieling.com/blog/parsing-pdfs-at-scale-with-node-js-pdf-js-and-lunr-js

var fracbotUrl = "{{site_url}}/fracbot";
var siteinfoUrl = "{{site_url}}/siteinfo";
var downloadAllTimeout = 5000; // seconds between each download...
var downloadAllPagesTimeout = 10000; // seconds to wait before doing a new search 

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
    if (top.document.autoupdate != undefined) top.document.autoupdate.updateStatus({msg: "Downloading..."});
    $.ajax({
        url: theForm.action,
        type: "POST",
        data:$(theForm).serialize(),
        xhrFields: {
            withCredentials: true
        },
        beforeSend: function(xhr) {
            xhr.overrideMimeType("text/plain; charset=x-user-defined");
        },
        success: function(data, textStatus, jqXHR) {
            $(row).find(".update").html('Uploading...');
            if (top.document.autoupdate != undefined) top.document.autoupdate.updateStatus({msg: "Uploading..."});
            // No idea why this mangling is necessary, but it is :S      
            var res = "";
            for (x=0; x < data.length; x++) res += String.fromCharCode(data.charCodeAt(x) & 0xff);
            data = res;
            globalData = data;
            globalTextStatus = textStatus;
            globalJqXHR = jqXHR;
            var api = $($(row).find("td")[2]).text();
        
            $.ajax({
                url: fracbotUrl + "/parse-pdf",
                type: "POST",
                data: {pdf: btoa(data), 'row': JSON.stringify(parseRow(row))},
                xhrFields: {
                    withCredentials: true
                },
                success: function (data, textStatus, jqXHR) {
                    globalParsedData = data;
                    updateRow(row, data);
                    if (top.document.autoupdate != undefined) top.document.autoupdate.updateStatus({items: 1, msg: "Downloaded."});
                    if (cb) cb(data);
                    console.log("pdf_upload_success on "+api);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $(row).find(".update").html('Failed :(');
                    if (top.document.autoupdate != undefined) top.document.autoupdate.updateStatus({failed: 1, msg: "Failed :("});
                    if (cb) cb();
                    console.log("pdf_upload_error on "+api);
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

function downloadRows(cb) {
    var rows = $("#MainContent_GridView1 tr:not(.PagerStyle):has(td.isnew)");
    var idx = -1;
    var next = function() {
        idx++;
        if (idx < rows.length) {
            downloadRow(rows[idx], function () {
                setTimeout(next, (Math.random+1)*downloadAllTimeout);
            });
        } else {
            cb();
        }
    }
    next();
}

function downloadAllPages(cb) {
    var downloadOneMorePage = function () {
        downloadRows(function () {
            var next = $("#MainContent_GridView1_ButtonNext");
            if (next.length > 0) {
                next.click();
            } else {
                $(document).off("pageUpdated", downloadOneMorePage);
                if (cb) {
                    setTimeout(cb, (Math.random()+1)*downloadAllPagesTimeout);
                } else {
                    console.log("Done downloading all pages");
                }
            }
        });
    }
    $(document).on("pageUpdated", downloadOneMorePage);
    downloadOneMorePage();
}

function getColumnHeadings() {
    return $("#MainContent_GridView1 tr:not(.PagerStyle) th").map(function (idx, col) { return $(col).text().trim(); });
}

function parseRow(row) {
    return zipToDict(getColumnHeadings(), $(row).find("td").map(function (idx, col) { return $(col).text().trim(); }))
}

function parseRows() {
    var res = [];
    $("#MainContent_GridView1 tr:not(.PagerStyle):not(:has(th)):not(:has(td[colspan=13]))").map(function (idx, row) {
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
    if (rowdata.event_guuid && $(row['Job Start Dt']).find("a").length == 0) {
        $(row['Job Start Dt']).wrapInner("<a href='" + siteinfoUrl + "/" + rowdata.event_guuid + "'>");
        $(row['']).append("<a target='_blank' href='" + siteinfoUrl + "/" + rowdata.event_guuid + "?style=csv'><img src='http://findicons.com/icon/download/84601/csv_text/48/png' style='border: none; width: auto; height: 30px;'></a>");
    }
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
   
    $.ajax({
        type: "POST",
        url: fracbotUrl + "/check-records",
        data: {records: JSON.stringify(parseRows())},
        xhrFields: {
            withCredentials: true
        },
        success: function (data, textStatus, jqXHR) {
            $("#MainContent_GridView1 tr:not(.PagerStyle):not(:has(th)):not(:has(td[colspan=13]))").map(function (idx, row) {
                updateRow(row, data[idx]);
            });
            $(document).trigger("pageUpdated");
            console.log("page_is_updated");
        },
        dataType: "json"
   });
}

function mangleResultsPage() {
    var btn = $("<a href='javascript:void(0);' class='BackToFilterButton'>Automatically update everything</a>");
    btn.click(downloadAllPages);
    $(".BackToFilterBox").append(btn);
    var rpm = Sys.WebForms.PageRequestManager.getInstance();
    rpm.add_endRequest(updatePage);
    if (top.document.autoupdate != undefined) {
        var autoUpdate = function () {
            $(document).off("pageUpdated", autoUpdate);
            downloadAllPages(function () {
                top.document.autoupdate.updateStatus({msg: "Searching...", state: '', county: '', counties: 1});
                document.location = "http://www.fracfocusdata.org/DisclosureSearch/StandardSearch.aspx";
            });
        };
        $(document).on("pageUpdated", autoUpdate);
    }
    updatePage();
}

function mangleSearchPage() {
    var tab = $("<div class='Tab'><a href='javascript:void(0);'>Automatically update SiteInfo</a></div>");
    $(".FindWellContainer").prepend(tab);
    $(".FindWellContainer").css({left: "500px"});
    tab.click(function () {
        $(".ContainerHeaderTitleFracFocus").html("Automcat update of SiteInfo in progress...")
        $(".ContainerBodyFracFocus *").remove();
        var status = $("<div class='autoupdatestatus'>Successfully updated <span class='items'></span> items. Update failed for <span class='failed'></span> items. Scraped <span class='counties'></span> counties so far.<br />State: <span class='state'></span>, County: <span class='county'></span><br /><span class='msg'></span></div><br /><div><a href='javascript:void(0);' class='show'>Show/hide automation screen...</a></div>");
        status.find(".pause").click(function () {

        });
        var updateStatusDisplay = function () {
            status.find(".items").html(document.autoupdate.items);
            status.find(".failed").html(document.autoupdate.failed);
            status.find(".counties").html(document.autoupdate.counties);
            status.find(".msg").html(document.autoupdate.msg);
            status.find(".state").html(document.autoupdate.state);
            status.find(".county").html(document.autoupdate.county);
        }
        document.autoupdate = {state: "search", msg: "Searching...", items: 0, failed: 0, counties: 0, state: '', county: '', updateStatus: function (data) {
            console.log(data);
            if (data.items) document.autoupdate.items += data.items;
            if (data.failed) document.autoupdate.failed += data.failed;
            if (data.counties) document.autoupdate.counties += data.counties;
            if (data.msg) document.autoupdate.msg = data.msg;
            if (data.state) document.autoupdate.state = data.state;
            if (data.county) document.autoupdate.county = data.county;
            updateStatusDisplay();
        }};
        updateStatusDisplay();
        $(".ContainerBodyFracFocus").append(status);
        var iframe = $("<iframe src='http://www.fracfocusdata.org/DisclosureSearch/StandardSearch.aspx'></iframe>");
        iframe.css({width: "100%", height: "400px", display: "none"});
        $(".ContainerBodyFracFocus").append(iframe);
        status.find(".show").click(function () {
            iframe.toggle();
        });
    });

    var rpm = Sys.WebForms.PageRequestManager.getInstance();
    rpm.add_endRequest(function () { update(); });

    var update = function () {
        var states = {};
        $("#MainContent_cboStateList option").map(function (idx, item) {
            if ($(item).val() != "Choose a State") {
                states[$(item).val()] = $(item).text();
            }
        });
        var countiesNr = 0;
        var counties = {};
        $("#MainContent_cboCountyList option").map(function (idx, item) {
            var value = $(item).val();
            if (value != "Choose a County" && value != "Choose a State First") {
                counties[value] = $(item).text();
                countiesNr++;
            }
        });
        if (countiesNr > 0) {
            var state = $("#MainContent_cboStateList").val();
            var stateName = states[state];
            $.ajax({
                type: "POST",
                url: fracbotUrl + "/update-counties",
                data: {arg: JSON.stringify({state: stateName, counties: counties})},
                xhrFields: {
                    withCredentials: true
                },
                success: function (data, textStatus, jqXHR) {
                    console.log(["update-counties-return", data]);
                },
                dataType: "json"
            });
        } else {
            $.ajax({
                type: "POST",
                url: fracbotUrl + "/update-states",
                data: {arg: JSON.stringify({states: states})},
                xhrFields: {
                    withCredentials: true
                },
                success: function (data, textStatus, jqXHR) {
                    console.log(["update-states-return", data]);
                },
                dataType: "json"
            });
        }
    }
    update();

}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

function autoupdateSearchPage() {
    var step = "state";

    var rpm = Sys.WebForms.PageRequestManager.getInstance();
    rpm.add_endRequest(function () { update(); });

    var update = function () {
        if (step == "state") {
            step = "county";
            var values = $("#MainContent_cboStateList option").map(function (idx, item) { return $(item).val(); }).filter(function (idx, item) { return item != "Choose a State"; });
            var value = values[getRandomInt(0, values.length - 1)];
            // value = "37"; // Pennsylvania
            top.document.autoupdate.updateStatus({state: $("#MainContent_cboStateList option[value=" + value + "]").text()});
            $("#MainContent_cboStateList").val(value);
            $("#MainContent_cboStateList").trigger("change");
        } else if (step == "county") {
            step = "submit";
            var values = $("#MainContent_cboCountyList option").map(function (idx, item) { return $(item).val(); }).filter(function (idx, item) { return item != "Choose a County"; });
            var value = values[getRandomInt(0, values.length - 1)];
            // value = "121" // Venango "117"; // Tioga
            top.document.autoupdate.updateStatus({county: $("#MainContent_cboCountyList option[value=" + value + "]").text()});
            $("#MainContent_cboCountyList").val(value);
            $("#MainContent_cboCountyList").trigger("change");
        } else if (step == "submit") {
            top.document.autoupdate.updateStatus({msg: "Getting list..."});
            $("#MainContent_btnSearch").click();
        }
    }
    update();
}

$(document).ready(function () {
    if ($(".BackToFilterBox").length > 0) {
        if ($("#MainContent_GridView1 tr").length > 1) {
            mangleResultsPage();
        }
    } else if ($(".BrowseFilterBox").length > 0) {
        if (top.document.autoupdate != undefined) {
            autoupdateSearchPage();
        } else {
            mangleSearchPage();
        }
    }
});
