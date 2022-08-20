import typing
# from threading import Thread

import PySimpleGUI as sg

win = None
types = {}

def _setattr(obj, key, val):
    obj.__dict__[key] = val

def _getwin(layout, cfg = {}):
    global win
    if win is not None and win.layout==layout:
        return win
    win = sg.Window(cfg.get('title', 'Colinxu2020\'s Toolbox'), layout = layout , resizable= cfg.get('resizable', True))
    _setattr(win, 'layout', layout)
    return win

def _choose_elm(key, ann, auto_update = False):
    try:
        name = ann.__name__
    except AttributeError:
        name = str(ann)
    else:
        if name is None:
            name = str(ann)
    if type(ann)==typing._LiteralGenericAlias:
        types[key]=name+':str'
        return sg.Combo(list(ann.__args__), key = key, enable_events=auto_update)
    if ann==typing.Any or issubclass(ann,(str,)):
         types[key]=name+':str'
         return  sg.In(key = key, enable_events=auto_update)
    if issubclass(ann, (list, dict)):
        types[key]=name+':eval'
        return sg.Multiline(key = key, enable_events=auto_update)
    if issubclass(ann, (bool,)):
       types[key]=name+':lambda x:True if x=="True" else False")'
       return sg.Combo(['True', 'False'], key = key, enable_events=auto_update)
    if issubclass(ann, (int, bytes)):
        types[key] = name + ':' + name 
        return sg.In(key = key, enable_events=auto_update)

    raise NotImplementedError('Bad thing... This function only support for Literal, any, str, int, bytes, list, bool or dict')

def conver_to_types(arg):
    rarg = {}
    for k,v in arg.items():
       try:
            rule = types[k]
            rarg[k] = eval(':'.join(rule.split(':')[1:]))(v)
       except KeyError:
            pass
    return rarg

def mainloop(win, auto_update = False):
    while msg:=win.read():
        print('new event:', *msg)
        if msg[0] is None:
            return win.close()
        if auto_update or msg[0]=='__submit__':
            try:
                win['__resp__'].update(types['def'](**conver_to_types(msg[1])))
            except (TypeError, ValueError):
                sg.Popup("数据值不符合要求\n"+'\n'.join(['数据:'+k+' 要求:'+v.split(':')[0] for k,v in types.items() if k!='def']))

def getgui(app, cfg = {}):
    layout = []
    types.clear()
    f_layout = [[sg.T('等待输出...', key='__resp__')]]
    auto_update = cfg.get('auto_submit', False)
    mode = cfg.get('mode', 'window')
    ann = typing.get_type_hints(app)
    template = cfg.get('template', [[sg.Frame('回显', layout=f_layout)]])
    ann.pop('return', '')
    for k, v in ann.items():
        layout.append([sg.T(k), _choose_elm(k, v, auto_update)])
    types['def'] = app
    if not auto_update:
        layout.append([sg.B('确定', key = '__submit__')])
    layout.append(template)
    if mode=='layout':
        return layout
    win = _getwin(layout, cfg)
    if mode=='window':
        return win
    mainloop(win,  auto_update)
