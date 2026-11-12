"""Normalize presentation literals without translating identifiers or actions."""
import json,re
from pathlib import Path
mapping=json.loads((Path(__file__).parent/"english-strings.json").read_text())
messages=json.loads((Path(__file__).parent/"messages-de.json").read_text())
known={**{v:k for k,v in messages.items() if v != k},**mapping,**{v:v for v in mapping.values()},**{v:v for v in messages}}
pattern=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
ui=re.compile(r'(?:text|label|title|subtitle|description|hint|placeholderText|supportingText|errorText|subtext|fallbackText|name|tooltip|toolTip|checkedText|overview)\s*:\s*[^;{}\n]*$',re.I)
def convert(text):
 def token(m):
  raw=m.group()
  if raw.startswith(('//','/*')) or raw[0]!='"':return raw
  try:value=json.loads(raw)
  except ValueError:return raw
  if value not in known:return raw
  prefix=text[max(0,m.start()-180):m.start()]
  # Existing translation calls retain their QML context; normalize German sources.
  if re.search(r'qsTr\(\s*$',prefix):return json.dumps(known[value],ensure_ascii=False)
  if re.search(r'(?:qsTranslate|i18n\w*)\([^\n]*$',prefix):return raw
  # Never translate machine values, comparison operands, paths or commands.
  if re.search(r'(?:===?|!==?|case|indexOf\(|includes\(|replace\(|command:|icon:|key:|id:|code:|value:|action:|type:|state:|status:|mode:|target:|category:)\s*$',prefix):return raw
  if re.search(r'(?:xdg|command|arguments|actions):\s*\[[^\]]*$', prefix): return raw
  if re.search(r'(?:replace|includes|indexOf)\([^)]*$', prefix): return raw
  if ui.search(prefix) or (' ' in value.strip() and not re.search(r'(?:import|source:|path:|command:)\s*$',prefix)):
   return 'qsTranslate("Flausen", '+json.dumps(known[value],ensure_ascii=False)+')'
  return raw
 result = pattern.sub(token,text)
 # Repair the two machine-value shapes used by the older migration.
 result = re.sub(r'((?:action|type|state|status|mode|target|category):\s*)qsTranslate\("Flausen", ("(?:[^"\\]|\\.)*")\)', r'\1\2', result)
 def machine_array(match):
  return re.sub(r'qsTranslate\("Flausen", ("(?:[^"\\]|\\.)*")\)', r'\1', match.group())
 result = re.sub(r'(?:xdg|command|arguments|actions):\s*\[[^\]]*\]', machine_array, result)
 if 'import qs.services' in result:
  result = result.replace('Qt.locale()', 'SystemLanguage.locale')
 result = result.replace('root.accessibleLabel + (root.muted ? qsTr(" einschalten") : qsTr(" stummschalten"))', '(root.muted ? qsTr("Enable %1") : qsTr("Mute %1")).arg(root.accessibleLabel)')
 result = result.replace('"Checked " + minutes + qsTranslate("Flausen", " min ago")', 'qsTranslate("Flausen", "Checked %1 min ago").arg(minutes)')
 result = result.replace('"Checked " + UpdateHub.stamp(oldest)', 'qsTranslate("Flausen", "Checked %1").arg(UpdateHub.stamp(oldest))')
 result = result.replace('"Downloading " + percent', 'qsTranslate("Flausen", "Downloading %1").arg(percent)')
 if 'readonly property int leadingDays:' in result and 'calendarLocale' in result:
  result = result.replace('(new Date(currYear, currMonth, 1).getDay() + 6) % 7', '(new Date(currYear, currMonth, 1).getDay() - calendarLocale.firstDayOfWeek + 7) % 7')
  result = result.replace('standaloneDayName(index + 1, Locale.ShortFormat)', 'standaloneDayName((root.calendarLocale.firstDayOfWeek + index) % 7, Locale.ShortFormat)')
  result = result.replace('color: index >= 5 ?', 'color: [0, 6].includes((root.calendarLocale.firstDayOfWeek + index) % 7) ?')
  result = result.replace('dayItem.index % 7 >= 5', '[0, 6].includes(dayItem.date.getDay())')
 if 'function details(key:' in result and 'function itemState(' in result:
  for expr in ['value.error', 'item.policy', 'item.detail', 'value.evidence']:
   result = result.replace(' + '+expr, ' + qsTranslate("Flausen", '+expr+')')
  result = result.replace('lines.push(value.evidence +', 'lines.push(qsTranslate("Flausen", value.evidence) +')
 if 'HermesSettingsPage' in result or 'root.loginProcess.running' in result:
  result = re.sub(r'(root\.message\s*=\s*)qsTranslate\("Flausen", ("(?:[^"\\]|\\.)*")\)', r'\1\2', result)
  result = result.replace('text:root.message;', 'text:qsTranslate("Flausen", root.message);')
 result = result.replace('subtitle: modelData.detail || ""', 'subtitle: qsTranslate("Flausen", modelData.detail || "")')
 # Date/time categories may differ from number formats in KDE.
 if 'HermesVramCard' not in result and 'function gib(bytes)' not in result:
  result = re.sub(r'(toLocale(?:Date|Time)?String\()SystemLanguage\.locale', r'\1SystemLanguage.timeLocale', result)
 result = result.replace('calendarLocale: SystemLanguage.locale', 'calendarLocale: SystemLanguage.timeLocale')
 result = result.replace('Qt.formatDateTime(date, SystemLanguage.locale)', 'Qt.formatDateTime(date, SystemLanguage.timeLocale)')
 if 'readonly property var languageOptions:' in result:
  result = result.replace('.arg(SystemLanguage.locale.name)', '.arg(SystemLanguage.language)')
 if 'framegenWrite.action' in result or 'blurSettings.command' in result:
  for state in ['on', 'off']:
   result = result.replace('qsTranslate("Flausen", "'+state+'")', '"'+state+'"')
 result = result.replace('SystemLanguage.timeLocale, "MMM d, HH:mm"', 'SystemLanguage.timeLocale, SystemLanguage.timeLocale.dateTimeFormat(Locale.ShortFormat)')
 result = result.replace('Time.date.toLocaleString(SystemLanguage.timeLocale, "ddd, MMM d")', 'Time.date.toLocaleDateString(SystemLanguage.timeLocale, "ddd, " + SystemLanguage.timeLocale.dateFormat(Locale.ShortFormat))')
 return result
