entity_id  = data.get('entity_id')
start_brightness = int(data.get('start_brightness'))
end_brightness = int(data.get('end_brightness'))
start_color = data.get('start_color')
end_color = data.get('end_color')
duration = int(data.get('duration_in_sec'))
steps = int(data.get('steps'))

def seq(start, stop, step=1):
    n = int(round((stop - start)/float(step)))
    if n > 1:
        return([start + step*i for i in range(n+1)])
    elif n == 1:
        return([start])
    else:
        return([])

def gamma_enc(x, g=2.2):
    return math.pow(x,1.0/g)

def gamma_dec(x, g=2.2):
    return math.pow(x,g)

delta_t = duration*1.0/steps

color = [0,0,0]
for i in seq(0.0,1.0,1.0/steps):
    color[0] = int(gamma_enc(gamma_dec(start_color[0])+(gamma_dec(end_color[0])-gamma_dec(start_color[0]))*i))
    color[1] = int(gamma_enc(gamma_dec(start_color[1])+(gamma_dec(end_color[1])-gamma_dec(start_color[1]))*i))
    color[2] = int(gamma_enc(gamma_dec(start_color[2])+(gamma_dec(end_color[2])-gamma_dec(start_color[2]))*i))
    b = start_brightness + (end_brightness-start_brightness)*i

    logger.info('Setting brightness of ' + str(entity_id) + ' to ' + str(b)+ ' and color to ' + str(color))
    data = { "entity_id" : entity_id, "brightness" : b, "rgb_color" : color }
    hass.services.call('light', 'turn_on', data)
    time.sleep(delta_t)

states = hass.states.get(entity_id)
current_brightness = states.attributes.get('brightness') or 0

if (current_brightness != end_brightness):
  logger.info('Setting brightness of ' + str(entity_id) + ' to ' + str(end_brightness))
  data = { "entity_id" : entity_id, "brightness" : end_brightness }
  hass.services.call('light', 'turn_on', data)


