"""Pack the skills as a Claude Desktop plugin: dist/TDMCP-Skills-<version>.zip

Standard library only. Claude Desktop installs it from Settings > Plugins >
Add > Upload a plugin; uploading a newer version replaces the installed one.
The archive is the plugin manifest plus skills/, README and licence. It
carries no .mcp.json: in Desktop the TouchDesigner connection comes from the
TDMCP.mcpb extension, not from the plugin.

    python build_plugin.py
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / 'dist'


def main():
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    manifest = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('version') != version:
        raise SystemExit('[plugin BLOCKED] plugin.json is {!r} but VERSION is {!r}; '
                         'run validate.py'.format(manifest.get('version'), version))
    files = [ROOT / '.claude-plugin' / 'plugin.json', ROOT / 'README.md', ROOT / 'LICENSE.md']
    files += sorted(p for p in (ROOT / 'skills').rglob('*') if p.is_file()
                    and not any(part.startswith('.') or part == '__pycache__'
                                for part in p.relative_to(ROOT).parts))
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / 'TDMCP-Skills-{}.zip'.format(version)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(ROOT).as_posix())
    skills = sorted({f.relative_to(ROOT).parts[1] for f in files if f.relative_to(ROOT).parts[0] == 'skills'})
    print('[plugin] wrote {} ({} bytes): {} skills, version {}'.format(out, out.stat().st_size, len(skills), version))


if __name__ == '__main__':
    main()
