/* Source: Codex skill ocean-city-hook (another machine), sent by Oxi 2026-11-10.
   Not yet run on the edit machine. Recipe and limits: references/after-effects.md section 11. */
/* Select text layers in an active AE comp. No save or render side effects. */
(function () {
    var comp = app.project.activeItem;
    if (!(comp instanceof CompItem)) { alert('Open a composition and select text layers.'); return; }
    var layers = comp.selectedLayers, count = 0;
    for (var n = 0; n < layers.length; n++) if (layers[n] instanceof TextLayer) count++;
    if (!count) { alert('Select at least one text layer.'); return; }
    var unit = comp.height / 1920;
    function shadow(fx, name, ratio, distance, softness) {
        var e = fx.property(name);
        if (!e) { e = fx.addProperty('ADBE Drop Shadow'); e.name = name; }
        if (e.matchName !== 'ADBE Drop Shadow') throw Error('Effect name collision: ' + name);
        e.enabled = true;
        e.property(1).setValue([0, 0, 0]);
        e.property(2).setValue(e.property(2).maxValue * ratio);
        e.property(3).setValue(135);
        e.property(4).setValue(distance * unit);
        e.property(5).setValue(softness * unit);
    }
    app.beginUndoGroup('Ocean City soft text V4');
    try {
        for (var i = 0; i < layers.length; i++) {
            var layer = layers[i]; if (!(layer instanceof TextLayer)) continue;
            var prop = layer.property('ADBE Text Properties').property('ADBE Text Document');
            if (prop.numKeys || prop.expressionEnabled) throw Error('Animated Source Text: adapt style per key manually: ' + layer.name);
            var doc = prop.value;
            var script = /script/i.test(layer.name) || /DancingScript/i.test(doc.font);
            doc.applyStroke = false; prop.setValue(doc);
            var fx = layer.property('ADBE Effect Parade');
            for (var k = 1; k <= fx.numProperties; k++) {
                var e = fx.property(k);
                if (e.matchName === 'ADBE Glo2') {
                    e.enabled = !script;
                    var wide = /wide/i.test(e.name);
                    e.property(3).setValue((wide ? 24 : 8) * unit);
                    e.property(4).setValue(wide ? 0.02 : 0.08);
                    e.property(7).setValue(2);
                    e.property(12).setValue(doc.fillColor);
                    e.property(13).setValue(doc.fillColor);
                }
            }
            shadow(fx, 'Drop Shadow | contact', script ? 0.80 : 0.72, script ? 4 : 6, script ? 7 : 10);
            shadow(fx, 'Drop Shadow | soft depth', 0.30, 12, 30);
        }
    } catch (error) { alert(error.toString() + '\nUse Undo to revert this group if needed.'); }
    finally { app.endUndoGroup(); }
})();
