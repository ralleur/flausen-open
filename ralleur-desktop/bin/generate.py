#!/usr/bin/env python3
"""Compile all theme consumers from design/tokens.json; no user writes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def wallpaper(t, mode):
    c, b = t['modes'][mode], t['brand']
    dark = mode == 'dark'
    # Original vector landscape, deliberately without windows or shell UI.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="2400" viewBox="0 0 1600 1000">
<title>Ralleur — Quiet Architecture / {mode}</title>
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{c['sky']}"/><stop offset="1" stop-color="{'#736152' if dark else '#CFC9BB'}"/></linearGradient>
 <linearGradient id="water" x2="0" y2="1"><stop stop-color="{c['water']}"/><stop offset="1" stop-color="{c['background']}"/></linearGradient>
 <linearGradient id="stone" x2=".8" y2="1"><stop stop-color="{'#3D4145' if dark else '#C9C8C0'}"/><stop offset="1" stop-color="{'#22292F' if dark else '#E5E2DA'}"/></linearGradient>
 <pattern id="ripples" width="113" height="9" patternUnits="userSpaceOnUse"><path d="M5 4H77 M90 7H112" stroke="{c['text']}" opacity=".055" stroke-width=".65"/></pattern>
</defs>
<rect width="1600" height="1000" fill="url(#sky)"/>
<circle cx="1120" cy="485" r="148" fill="{b['amber']}" opacity="{'0.58' if dark else '0.52'}"/>
<path d="M0 630L100 580L220 617L382 545L540 615L690 592L843 639L1005 529L1123 594L1280 611L1436 548L1600 515V800H0Z" fill="{c['hill']}" opacity=".48"/>
<path d="M0 653L152 606L335 647L514 603L719 656L924 613L1042 564L1195 637L1324 616L1461 572L1600 549V801H0Z" fill="{c['hill']}"/>
<path d="M0 700Q550 660 1000 684T1600 690V1000H0Z" fill="url(#water)"/>
<path d="M0 710Q600 670 1600 700V1000H0Z" fill="url(#ripples)"/>
<path d="M0 817L336 734L701 745L1600 903V1000H0Z" fill="url(#stone)"/>
<path d="M0 879L534 781L1600 963M87 1000L531 781M742 1000L791 825" fill="none" stroke="{c['text']}" stroke-width="1" opacity=".24"/>
<path d="M0 720H224V609H325V719H761V835H0Z" fill="url(#stone)"/>
<path d="M224 609L263 588H360L325 609V719H289V609" fill="{c['stroke']}" opacity=".7"/>
<path d="M1167 94V799M1170 94V799M921 809V950" stroke="{c['text']}" stroke-width=".8" fill="none" opacity=".42"/>
<path d="M898 821A435 435 0 0 1 1589 121M911 828A435 435 0 0 1 1589 145" stroke="{c['text']}" stroke-width=".7" fill="none" opacity=".4"/>
<circle cx="857" cy="363" r="42" fill="{b['red']}" opacity=".85"/>
<circle cx="903" cy="535" r="54" fill="{b['blue']}" opacity=".8"/>
<path d="M154 642v-77m0 39l-23-24m23 13l26-34" stroke="{c['hill']}" stroke-width="5"/>
<g fill="{b['green']}" opacity=".68"><circle cx="129" cy="571" r="19"/><circle cx="158" cy="554" r="26"/><circle cx="179" cy="577" r="20"/></g>
</svg>'''


def scheme(t, mode):
    c, b = t['modes'][mode], t['brand']
    colors = {}
    for key in ['background', 'surface', 'surfaceDim', 'surfaceBright', 'surfaceContainerLowest', 'surfaceContainerLow', 'surfaceContainer', 'surfaceContainerHigh', 'surfaceContainerHighest', 'surfaceVariant']:
        colors[key] = c['surface'] if key in ('background', 'surface') else c['elevated']
    for key in ['onBackground', 'onSurface', 'onPrimaryContainer', 'onSecondaryContainer', 'onTertiaryContainer']:
        colors[key] = c['text']
    colors.update(onSurfaceVariant=c['muted'], outline=c['muted'], outlineVariant=c['stroke'], shadow='#000000', scrim='#000000', surfaceTint=c['focus'], primary=c['focus'], onPrimary=c['background'], primaryContainer=c['elevated'], secondary=b['teal'], onSecondary='#FFFFFF', secondaryContainer=c['elevated'], tertiary=b['amber'], onTertiary='#17191B', tertiaryContainer=c['elevated'], error=b['red'], onError='#FFFFFF', errorContainer=c['elevated'], onErrorContainer=c['text'], inverseSurface=c['text'], inverseOnSurface=c['background'], inversePrimary=c['focus'], success=b['green'], onSuccess='#FFFFFF', successContainer=c['elevated'], onSuccessContainer=c['text'])
    for role in ['primary', 'secondary', 'tertiary']:
        colors.update({role+'Fixed': c['elevated'], role+'FixedDim': c['stroke'], 'on'+role.title()+'Fixed': c['text'], 'on'+role.title()+'FixedVariant': c['muted']})
    ansi = [c['background'], b['red'], b['green'], b['amber'], c['focus'], '#B4ACF0', b['teal'], c['text']]
    colors.update({f'term{i}': value for i, value in enumerate(ansi + ansi)})
    return {'name': 'Ralleur', 'flavour': 'quiet-architecture', 'mode': mode, 'colours': {k:v.lstrip('#') for k,v in colors.items()}}


def generate():
    t = json.loads((ROOT/'design/tokens.json').read_text())
    g, fx = t['geometry'], t['effects']
    shell = json.loads((ROOT/'config/shell.json').read_text())
    shell['border'] = {'thickness':g['frame'], 'rounding':g['windowRadius']+4, 'smoothing':12}
    shell['appearance']['font'] = {k: {'family':t['typography']['ui']} for k in ('body','label','title','headline')}
    shell['appearance']['font']['mono'] = {'family':t['typography']['mono']}
    write(ROOT/'build/shell.json', json.dumps(shell, indent=2)+'\n')
    for mode, c in t['modes'].items():
        out = ROOT/'build/modes'/mode
        write(ROOT/f'assets/wallpapers/ralleur-{mode}.svg', wallpaper(t, mode))
        write(out/'scheme.json', json.dumps(scheme(t, mode), indent=2)+'\n')
        b = t['brand']
        ansi = [c['background'], b['red'], b['green'], b['amber'], c['focus'], '#B4ACF0', b['teal'], c['text']]
        kitty = f"background {c['surface']}\nforeground {c['text']}\nselection_background {c['focus']}\nselection_foreground {c['background']}\ncursor {c['text']}\n"
        kitty += ''.join(f'color{i} {v}\n' for i, v in enumerate(ansi+ansi))
        write(out/'kitty.conf', kitty)
        gtk = '\n'.join(f'@define-color {name} {value};' for name,value in {'theme_bg_color':c['surface'], 'theme_fg_color':c['text'], 'theme_base_color':c['background'], 'theme_text_color':c['text'], 'theme_selected_bg_color':c['focus'], 'theme_selected_fg_color':c['background'], 'borders':c['stroke']}.items())
        gtk += f'\nwindow, .background {{ background-color: {c["surface"]}; color: {c["text"]}; }}\nheaderbar {{ background: {c["elevated"]}; color: {c["text"]}; box-shadow: none; }}\n*:focus-visible {{ outline-color: {c["focus"]}; }}\n'
        write(out/'gtk.css', gtk)
        write(out/'gtk-settings.ini', '[Settings]\ngtk-theme-name=Adwaita'+('-dark' if mode=='dark' else '')+'\ngtk-icon-theme-name=breeze\ngtk-font-name=Inter 10\ngtk-application-prefer-dark-theme='+('1' if mode=='dark' else '0')+'\n')
        # QPalette role order from Qt; qt6ct reads a complete list for each group.
        palette = [c['text'],c['surface'],c['elevated'],c['elevated'],c['stroke'],c['stroke'],c['text'],c['text'],c['text'],c['background'],c['surface'],'#000000',c['focus'],c['background'],c['focus'],b['teal'],c['elevated'],c['text'],c['elevated'],c['text'],c['muted'],c['focus']]
        write(out/'qt6ct-colors.conf', '[ColorScheme]\n'+''.join(f'{group}_colors='+', '.join(palette)+'\n' for group in ('active','inactive','disabled')))
        # KColorSchemeManager consumes this for KDE applications launched with the session.
        kcolors = '[General]\nName=Ralleur '+mode+'\nColorScheme=Ralleur\n'+''.join(f'[Colors:{role}]\nBackgroundNormal={c[bg]}\nBackgroundAlternate={c[bg]}\nForegroundNormal={c[fg]}\nForegroundInactive={c["muted"]}\nDecorationFocus={c["focus"]}\nDecorationHover={c["focus"]}\n' for role,bg,fg in [('Window','surface','text'),('View','background','text'),('Button','elevated','text'),('Selection','focus','background'),('Tooltip','elevated','text'),('Header','elevated','text')])
        import re
        kcolors = re.sub(r'#[0-9A-Fa-f]{6}', lambda m: ','.join(str(int(m[0][i:i+2],16)) for i in (1,3,5)), kcolors)
        write(out/'Ralleur.colors', kcolors)
        write(out/'kdeglobals', kcolors+'[KDE]\nwidgetStyle=Fusion\n[Icons]\nTheme=breeze\n')
        konsole = '[General]\nDescription=Ralleur '+mode+'\nOpacity=1\n'
        def rgb(h): return ','.join(str(int(h[i:i+2],16)) for i in (1,3,5))
        konsole += f'[Background]\nColor={rgb(c["surface"])}\n[Foreground]\nColor={rgb(c["text"])}\n'
        konsole += ''.join(f'[Color{i}{suffix}]\nColor={rgb(v)}\n' for suffix in ('','Intense','Faint') for i,v in enumerate(ansi))
        write(out/'Ralleur.colorscheme', konsole)
        write(out/'firefox-user.js', 'user_pref("browser.theme.content-theme", '+('0' if mode=='dark' else '1')+');\nuser_pref("browser.theme.toolbar-theme", '+('0' if mode=='dark' else '1')+');\nuser_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);\n')
        write(out/'userChrome.css', f':root {{ --toolbar-bgcolor: {c["surface"]} !important; --toolbar-color: {c["text"]} !important; --lwt-accent-color: {c["background"]} !important; --lwt-text-color: {c["text"]} !important; }}\n')
        # Both formats are generated. Lua is the default for Hyprland >=0.55.
        conf = f'''general {{
    gaps_in = {g['gap']//2}
    gaps_out = {g['gap']}
    border_size = 1
    col.active_border = rgb({c['focus'][1:]})
    col.inactive_border = rgb({c['stroke'][1:]})
    layout = dwindle
    resize_on_border = true
}}
decoration {{
    rounding = {g['windowRadius']}
    active_opacity = 1.0
    inactive_opacity = 1.0
    shadow {{
        enabled = true
        range = {fx['shadowRange']}
        render_power = 3
        color = rgba(000000{round(fx['shadowOpacity']*255):02x})
    }}
    blur {{
        enabled = true
        size = {fx['blurSize']}
        passes = {fx['blurPasses']}
    }}
}}
animations {{
    enabled = false
}}
dwindle {{
    preserve_split = true
}}
'''
        write(out/'hypr-theme.conf', conf)
        lua = f'''hl.config({{
 general = {{ gaps_in = {g['gap']//2}, gaps_out = {g['gap']}, border_size = 1, layout = "dwindle", resize_on_border = true,
   col = {{ active_border = "rgb({c['focus'][1:]})", inactive_border = "rgb({c['stroke'][1:]})" }} }},
 decoration = {{ rounding = {g['windowRadius']}, active_opacity = 1.0, inactive_opacity = 1.0,
   shadow = {{ enabled = true, range = {fx['shadowRange']}, render_power = 3, color = "rgba(000000{round(fx['shadowOpacity']*255):02x})" }},
   blur = {{ enabled = true, size = {fx['blurSize']}, passes = {fx['blurPasses']} }} }},
 animations = {{ enabled = false }}, dwindle = {{ preserve_split = true }}
}})
'''
        write(out/'hypr-theme.lua', lua)
    return t


if __name__ == '__main__':
    generate()
