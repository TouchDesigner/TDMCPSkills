"""Pack the skills as a Claude plugin archive: dist/TDMCP-Skills-<version>.zip

Standard library only. The archive is the plugin manifest plus skills/, README
and licence, with no .mcp.json. Its consumer is the TDMCP build
(scripts/build_mcpb.py in TDMCP), which takes the skills/ tree from the zip
attached to the release it pins and packs it into Derivative-TDMCP.plugin, the
one plugin Claude Desktop users install. Text is packed with LF line endings.

    python build_plugin.py
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / 'dist'
# Packed with LF line endings whatever the checkout has: a Windows clone made
# before .gitattributes existed still holds CRLF working copies.
TEXT_SUFFIXES = {'.md', '.json', '.txt', '.py', '.glsl', '.html', '.yaml', '.yml'}


def packed_bytes(path):
    """The file's bytes as they go into the archive: text with LF endings."""
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b'\r\n', b'\n')
        if b'\r' in data:
            raise SystemExit('[plugin BLOCKED] {} contains a bare CR; save it with LF '
                             'line endings'.format(path.relative_to(ROOT).as_posix()))
    return data


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
            z.writestr(f.relative_to(ROOT).as_posix(), packed_bytes(f))
    skills = sorted({f.relative_to(ROOT).parts[1] for f in files if f.relative_to(ROOT).parts[0] == 'skills'})
    print('[plugin] wrote {} ({} bytes): {} skills, version {}'.format(out, out.stat().st_size, len(skills), version))


if __name__ == '__main__':
    main()
