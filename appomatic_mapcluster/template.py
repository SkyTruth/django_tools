# -*- coding: utf-8 -*-

def template_reports_mangle_row(columns, row):
    pass

def template_reports_colorcolumn(columns):
    return u"color"

def template_reports_colors(columns):
    # Colors are Alpha, Blue, Gree, Red (same order as KML)
    return {
        "mincolor": (255, 00, 255, 255),
        "maxcolor": (255, 00, 255, 255),
        "nonecolor": (255, 0, 255, 255)}

def template_reports_name():
    return u"Reports"

def template_reports_description():
    return u'All reports'

def template_cluster_mangle_row(columns, row):
    pass

def template_cluster_colorcolumn(columns):
    return u"color_avg"

def template_cluster_colors(columns):
    # Colors are Alpha, Blue, Gree, Red (same order as KML)
    return {
        "mincolor": (255, 00, 255, 255),
        "maxcolor": (255, 00, 255, 255),
        "nonecolor": (255, 0, 255, 255)}

def template_cluster_name(columns):
    return u""

def template_cluster_description(columns):
    columnnames = columns.keys()
    columnnames.sort()
    description = []
    for name in columnnames:
        t = columns[name]
        if name == 'id': continue
        if t == 'NUMBER':
            description.append('<tr><th>%s (min)</th><td>%%(%s_min)s' % (name, name))
            description.append('<tr><th>%s (max)</th><td>%%(%s_max)s' % (name, name))
            description.append('<tr><th>%s (avg)</th><td>%%(%s_avg)s' % (name, name))
            description.append('<tr><th>%s (stddev)</th><td>%%(%s_stddev)s' % (name, name))
        elif t == 'DATETIME':
            description.append('<tr><th>%s (min)</th><td>%%(%s_min)s' % (name, name))
            description.append('<tr><th>%s (max)</th><td>%%(%s_max)s' % (name, name))
            description.append('<tr><th>%s (avg)</th><td>%%(%s_avg)s' % (name, name))
            description.append('<tr><th>%s (stddev)</th><td>%%(%s_stddev)s' % (name, name))
    return '<h2>%(count)s</h2><table>' + ''.join(description) + '</table>'

def template_report_name(columns):
    return u""

def template_report_description(columns):
    columnnames = columns.keys()
    columnnames.sort()
    description = []
    for name in columnnames:
        if name == 'id': continue
        description.append('<tr><th>%s</th><td>%%(%s)s' % (name, name))
    return '<h2>%(id)s</h2><table>' + ''.join(description) + '</table>'
