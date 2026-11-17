"""Fallback channel to Premiere when the cloud MCP host is down or lacks a tool.

The `MCP Bridge (CEP)` panel is a file-drop IPC: it polls a temp directory,
runs any `cmd_<id>.jsx` it finds, and writes the returned string to
`res_<id>.json`. It does not care which process wrote the command, so this
module can drive Premiere directly with no MCP server in the loop.

Use it when either is true:

  * the cloud host reports the app disconnected and Oxi needs work done now;
  * the operation has no MCP tool at all. Verified gaps as of 2026-08-10:
    relinking media (`projectItem.changeMediaPath`), `setOffline`, refreshing
    a project item, attaching/detaching a proxy, and running raw ExtendScript.

Prefer a dedicated MCP tool whenever one exists; this is the escape hatch, not
the default route. Everything in `premiere-mcp.md` about mutation verification
still applies - snapshot the affected items, mutate, then read the same fields
back from a FRESH query and fail closed on any difference.

Usage:
    from pr_file_bridge import run, ok
    data = ok(run('return __result(__q(app.project.name));'))

    python pr_file_bridge.py --ping
    python pr_file_bridge.py --file probe.jsx

The panel must be running and showing `Bridge started` for any of this to work.
"""
import argparse
import json
import os
import sys
import time

DEFAULT_TEMP = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"),
                            "premiere-mcp-bridge")

# Deliberately NOT the helper block shipped inside premiere-pro-mcp. That one
# falls back to a hand-rolled stringifier whose escapes are only correct after
# JavaScript has parsed the template literal it lives in, and Premiere's
# ExtendScript cannot be relied on to provide a native JSON to skip that path.
# Everything below is plain ES3 and escapes non-ASCII to \uXXXX, so Vietnamese
# bin, clip and folder names survive the round trip whatever encoding the panel
# writes the response file in.
HELPERS = r"""
function __q(s) {
  if (s === null || s === undefined) return "null";
  s = String(s);
  var o = "", i, c, n, h;
  for (i = 0; i < s.length; i++) {
    c = s.charAt(i);
    n = s.charCodeAt(i);
    if (c == '"') o += '\\"';
    else if (c == '\\') o += '\\\\';
    else if (c == '\n') o += '\\n';
    else if (c == '\r') o += '\\r';
    else if (c == '\t') o += '\\t';
    else if (n < 32 || n > 126) {
      h = n.toString(16);
      while (h.length < 4) h = "0" + h;
      o += '\\u' + h;
    } else o += c;
  }
  return '"' + o + '"';
}
function __kv(pairs) {
  var p = [], i;
  for (i = 0; i < pairs.length; i++) p.push(__q(pairs[i][0]) + ":" + pairs[i][1]);
  return "{" + p.join(",") + "}";
}
function __arr(items) { return "[" + items.join(",") + "]"; }
function __num(x) { return String(x); }
function __bool(x) { return x ? "true" : "false"; }
function __result(payload) { return '{"success":true,"data":' + payload + '}'; }
function __error(msg) { return '{"success":false,"error":' + __q(msg) + '}'; }

// Collect the project tree into a flat array. type 1 = clip, 2 = bin, 3 = root.
// Descend on "has children", NOT on `type == 2`: app.project.rootItem is type 3,
// so a `type == 2` guard stops dead at the root and returns a one-item array
// with no error raised. That silent empty walk cost real time on 2026-08-10.
function __flatten(item) {
  var out = [], stack = [item], cur, i;
  while (stack.length) {
    cur = stack.pop();
    out.push(cur);
    if (cur.children && cur.children.numItems) {
      for (i = 0; i < cur.children.numItems; i++) stack.push(cur.children[i]);
    }
  }
  return out;
}
// Resolve a bin by name anywhere in the tree; returns null when absent so the
// caller can fail loudly instead of mutating the wrong bin.
function __findBin(name) {
  var all = __flatten(app.project.rootItem), i;
  for (i = 0; i < all.length; i++) {
    if (all[i].type == 2 && all[i].name == name) return all[i];
  }
  return null;
}
"""


def temp_dir():
    return os.environ.get("PREMIERE_TEMP_DIR") or DEFAULT_TEMP


def run(code, timeout=120.0, poll=0.1, tempdir=None):
    """Send one ExtendScript body; return the parsed {success, data|error}.

    `code` runs inside a try/catch and must end in `return __result(...)`.
    """
    raise RuntimeError(
        "RETIRED by Oxi 2026-11-02: MCP Bridge file panel is disabled. "
        "Use Higgsfield https://bridge.higgsfield.ai/mcp (get_host_status then pr_*). "
        "Do not reinstall MCPBridgeCEP or retry this transport."
    )
    td = tempdir or temp_dir()
    if not os.path.isdir(td):
        raise RuntimeError("bridge temp dir missing: %s - is the panel running?" % td)
    cid = "%d_%d" % (time.time() * 1000, os.getpid() % 100000)
    cmd = os.path.join(td, "cmd_%s.jsx" % cid)
    res = os.path.join(td, "res_%s.json" % cid)
    script = HELPERS + "\n(function(){\ntry {\n" + code + \
        "\n} catch(e) { return __error(e.toString()); }\n})();"
    with open(cmd, "w", encoding="utf-8") as fh:
        fh.write(script)
    start = time.time()
    try:
        while True:
            if os.path.exists(res):
                # The panel may still be mid-write; retry briefly rather than
                # report a truncated file as a failed command.
                for _ in range(20):
                    try:
                        with open(res, encoding="utf-8") as fh:
                            return json.load(fh)
                    except Exception:
                        time.sleep(0.05)
                with open(res, encoding="utf-8") as fh:
                    return {"success": False,
                            "error": "unparsable response: " + fh.read()[:400]}
            if time.time() - start > timeout:
                return {"success": False,
                        "error": "timed out after %.0fs - panel running?" % timeout}
            time.sleep(poll)
    finally:
        for p in (cmd, res):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except OSError:
                pass


def ok(r):
    """Unwrap a result, raising on failure so a bad step cannot pass silently."""
    if not r.get("success"):
        raise RuntimeError(r.get("error", "unknown bridge error"))
    return r["data"]


def esc(s):
    """Escape a Windows path or name for embedding in an ExtendScript literal."""
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ping", action="store_true",
                    help="report the open project, proving the panel answers")
    ap.add_argument("--file", help="run an ExtendScript body from a file")
    ap.add_argument("--timeout", type=float, default=120.0)
    a = ap.parse_args()

    if a.ping:
        code = ('return __result(__kv([["project", __q(app.project.name)],'
                '["path", __q(app.project.path)]]));')
    elif a.file:
        with open(a.file, encoding="utf-8") as fh:
            code = fh.read()
    else:
        ap.error("pass --ping or --file")

    r = run(code, timeout=a.timeout)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
