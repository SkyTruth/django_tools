import csv as csvlib
import StringIO


def convert(rows):
    buffer = StringIO.StringIO()
    writer = csvlib.writer(buffer)

    headers = None
    for row in rows:
        del row['location']
        if not headers:
            headers = row.keys()
            headers.sort()
            writer.writerow(headers)
        writer.writerow([row[header] for header in headers])
    return buffer.getvalue()
