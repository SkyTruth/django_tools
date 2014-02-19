import PIL
import StringIO
import django.http
import os.path
import numpy

def readcolor(x):
    return tuple(int(y, 16) for y in (x[0:2], x[2:4], x[4:6])) + (255,)

def icon(request):
    angle = -float(request.GET.get("angle", "0"))
    orig_color = (255,255,255,255)
    replacement_color = readcolor(request.GET.get("color", "ffffff"))

    img = PIL.Image.open(os.path.join(os.path.dirname(__file__), "icon.png")).convert('RGBA')

    img = img.rotate(angle, expand=1 )

    data = numpy.array(img)
    data[(data == orig_color).all(axis = -1)] = replacement_color
    img = PIL.Image.fromarray(data, mode = 'RGBA')

    out = StringIO.StringIO()
    img.save(out, "png")
    return django.http.HttpResponse(out.getvalue(), content_type="image/png")
