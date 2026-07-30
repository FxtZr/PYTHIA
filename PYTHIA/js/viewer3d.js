/* PYTHIA -- 3D structure viewer.
 *
 * A thin layer over 3Dmol.js. Its only real job is to keep the 3D view and
 * the 2D drawing talking to each other.
 *
 * The index correspondence is what makes that possible, and it is worth
 * stating plainly because everything here depends on it:
 *
 *   The build step writes the 2D drawing from the kekulised molecule and
 *   the 3D block from the same molecule after adding hydrogens. RDKit's
 *   AddHs appends, it does not reorder, so heavy atom i in the drawing is
 *   atom i in the 3D block. Hydrogens occupy the indices after the last
 *   heavy atom and have no counterpart in the drawing.
 *
 * If that ever stops holding, atom highlighting will point at the wrong
 * atom rather than fail loudly, so treat it as load-bearing.
 */
(function (root) {
  "use strict";

  var STYLE_BASE = { stick: { radius: 0.13 }, sphere: { scale: 0.20 } };

  function themeColours() {
    var s = getComputedStyle(document.documentElement);
    return {
      background: s.getPropertyValue("--paper").trim() || "#faf9f6",
      accent: s.getPropertyValue("--accent").trim() || "#2c4a63",
      ink: s.getPropertyValue("--ink").trim() || "#1a1917"
    };
  }

  function Viewer3D(host) {
    this.host = host;
    this.viewer = null;
    this.available = typeof root.$3Dmol !== "undefined";
    this.marked = null;
  }

  Viewer3D.prototype.load = function (sdf) {
    if (!this.available) {
      this.host.innerHTML = "";
      var msg = document.createElement("p");
      msg.className = "hint";
      msg.textContent = "The 3D viewer could not start. Check that "
        + "assets/vendor/3Dmol-min.js is present.";
      this.host.appendChild(msg);
      return false;
    }

    var colours = themeColours();
    if (!this.viewer) {
      this.viewer = root.$3Dmol.createViewer(this.host, {
        backgroundColor: colours.background,
        antialias: true
      });
    }
    this.viewer.clear();
    this.viewer.setBackgroundColor(colours.background);
    this.viewer.addModel(sdf, "sdf");
    this.viewer.setStyle({}, STYLE_BASE);
    this.viewer.zoomTo();
    this.viewer.render();
    this.marked = null;
    return true;
  };

  /* Emphasise one atom, given its index in the 2D drawing. Passing null
   * clears the emphasis. */
  Viewer3D.prototype.mark = function (index) {
    if (!this.viewer) return;
    if (this.marked === index) return;
    this.marked = index;

    this.viewer.setStyle({}, STYLE_BASE);
    if (index !== null && index !== undefined) {
      var colours = themeColours();
      this.viewer.addStyle({ index: index }, {
        sphere: { scale: 0.42, color: colours.accent }
      });
    }
    this.viewer.render();
  };

  /* Spin, for readers trying to see that a molecule and its mirror image
   * are genuinely not superimposable. Off by default: motion nobody asked
   * for is a nuisance, and it is disabled outright when the reader has
   * asked for reduced motion. */
  Viewer3D.prototype.spin = function (on) {
    if (!this.viewer) return false;
    var reduce = root.matchMedia
      && root.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (on && reduce) return false;
    this.viewer.spin(on ? "y" : false);
    return !!on;
  };

  Viewer3D.prototype.resize = function () {
    if (this.viewer) this.viewer.resize();
  };

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.Viewer3D = Viewer3D;
})(typeof window !== "undefined" ? window : this);
