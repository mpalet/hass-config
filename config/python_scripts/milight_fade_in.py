mqtt_topic = data.get('mqtt_topic')
colors = data.get('colors')
color_temp = data.get('color_temp')
duration = int(data.get('duration_in_sec'))

def seq(start, stop, step=1):
    n = int(round((stop - start)/float(step)))
    if n > 1:
        return([start + step*i for i in range(n+1)])
    elif n == 1:
        return([start])
    else:
        return([])

def gamma_enc(x, g=1.2):
    return math.pow(x,1.0/g)

def gamma_dec(x, g=1.2):
    return math.pow(x,g)

def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
      r, g, b = v, t, p
    elif hi == 1:
      r, g, b = q, v, p
    elif hi == 2:
      r, g, b = p, v, t
    elif hi == 3:
      r, g, b = p, q, v
    elif hi == 4:
      r, g, b = t, p, v
    elif hi == 5:
      r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

last_h = 0
def rgb2hsv(r, g, b):
    def maximum(a,b,c):
      r = a
      if (b > a):
        r = b
      if (c > r):
        r = c
      return r
    def minimum(a,b,c):
      r = a
      if (b < a):
        r = b
      if (c < r):
        r = c
      return r

    global last_h
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = maximum(r, g, b)
    mn = minimum(r, g, b)
    df = mx-mn
    if mx == mn:
        #h = 0
        h = last_h
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx

    last_h = h
    return h, s, v

delta_t = 0.5
steps = duration*1.0/delta_t
partial_steps = steps/(len(colors)-1)

payload = '{\"state\":\"OFF\", \"level\":0, \"color_temp\":%d, \"state\":\"ON\"}' % (color_temp)
hass.services.call('mqtt', 'publish', { "topic" : mqtt_topic, "payload": payload })
#time.sleep(delta_t)
for i in range(len(colors)-1):
    start_color = colors[i]
    end_color = colors[i+1]
    for i in seq(0.0,1.0,1.0/partial_steps):
        r = int(gamma_enc(gamma_dec(start_color[0])+(gamma_dec(end_color[0])-gamma_dec(start_color[0]))*i))
        g = int(gamma_enc(gamma_dec(start_color[1])+(gamma_dec(end_color[1])-gamma_dec(start_color[1]))*i))
        b = int(gamma_enc(gamma_dec(start_color[2])+(gamma_dec(end_color[2])-gamma_dec(start_color[2]))*i))
        h,s,v = rgb2hsv(r,g,b)
        h = int(h)
        s = int(s*100)
        v = int(v*100)

        #logger.info('Setting brightness of ' + str(mqtt_topic) + ' to ' + str(v) + ' and color to ' + str([r,g,b]))
        payload = '{\"level\":' + str(v) + ',\"hue\":' + str(h) + \
              ',\"saturation\":' + str(s) + '}'
        hass.services.call('mqtt', 'publish', { "topic" : mqtt_topic, "payload": payload })
        #payload = '{\"state\":\"ON\"}'
        #hass.services.call('mqtt', 'publish', { "topic" : mqtt_topic, "payload": payload })
        time.sleep(delta_t)

if s == 999: #s=0 not working problems
    payload = '{\"command\":\"set_white\",\"level\":%d}' % (v)
    hass.services.call('mqtt', 'publish', { "topic" : mqtt_topic, "payload": payload })
