/* PYTHIA -- the Stereochemistry view.
 *
 * The lessons, with every molecule they mention drawn where it is
 * mentioned. A reader who has to hold a structure in their head while
 * reading about it is doing two jobs at once, and the second one is the
 * one that fails.
 *
 * Any structure here can be clicked to open it in Explore, where it can be
 * turned in space.
 */
(function (root) {
  "use strict";

  var state = { id: null };

  function h(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === "class") node.className = attrs[k];
        else if (k === "text") node.textContent = attrs[k];
        else if (attrs[k] !== null && attrs[k] !== undefined) {
          node.setAttribute(k, attrs[k]);
        }
      }
    }
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  function lessons() { return root.PYTHIA_LESSONS || []; }

  function molecule(id) {
    var all = root.PYTHIA_MOLECULES || [];
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  function find(id) {
    var all = lessons();
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  /* ---- a structure, drawn inline and clickable ------------------------ */

  function card(id) {
    var m = molecule(id);
    if (!m) {
      // the build checks for this, so reaching here means data went stale
      return h("div", { class: "example-card" }, [
        h("p", { class: "hint", text: "Missing structure: " + id })
      ]);
    }

    var svg = root.PYTHIA.depict(m.d2, {
      bondLength: 30,
      highlight: m.centres.map(function (c) { return c.atom; })
    });
    svg.setAttribute("aria-label", "Structure of " + m.name);

    var btn = h("button", {
      type: "button",
      class: "example-open",
      title: "Open " + m.name + " in Explore"
    }, [
      svg,
      h("span", { class: "example-name", text: m.common || m.name })
    ]);

    btn.addEventListener("click", function () {
      if (root.PYTHIA.views.explore && root.PYTHIA.views.explore.open) {
        root.PYTHIA.views.explore.open(m.id);
      }
    });

    return h("div", { class: "example-card" }, [btn]);
  }

  function renderBlock(block) {
    if (block.kind === "text") {
      return h("p", { class: "lesson-text", text: block.text });
    }

    if (block.kind === "callout") {
      return h("div", { class: "callout" }, [
        h("p", { class: "label", text: block.title }),
        h("p", { text: block.text })
      ]);
    }

    if (block.kind === "examples" || block.kind === "compare") {
      var row = h("div", {
        class: block.kind === "compare" ? "example-row is-pair" : "example-row"
      });
      block.ids.forEach(function (id) { row.appendChild(card(id)); });

      var wrap = [row];
      if (block.caption) {
        wrap.push(h("p", { class: "example-caption", text: block.caption }));
      }
      return h("figure", { class: "lesson-figure" }, wrap);
    }

    return null;
  }

  /* ---- browser --------------------------------------------------------- */

  function renderBrowser(onPick) {
    var wrap = h("div", { class: "browser" });
    var list = h("div", { class: "group-list" });
    list.appendChild(h("p", { class: "label group-name", text: "Lessons" }));

    var ul = h("ul", { class: "mol-list" });
    lessons().forEach(function (l, i) {
      var btn = h("button", {
        type: "button",
        text: (i + 1) + ". " + l.title,
        "aria-current": l.id === state.id ? "true" : null
      });
      btn.addEventListener("click", function () { onPick(l.id); });
      ul.appendChild(h("li", null, [btn]));
    });
    list.appendChild(ul);
    wrap.appendChild(list);
    return wrap;
  }

  /* ---- assembly -------------------------------------------------------- */

  function renderLesson(lesson, index, total) {
    var kids = [
      h("div", { class: "section-head" }, [
        h("h2", { text: lesson.title }),
        h("p", { text: "Lesson " + index + " of " + total })
      ]),
      h("p", { class: "lesson-blurb", text: lesson.blurb })
    ];

    lesson.blocks.forEach(function (b) {
      var node = renderBlock(b);
      if (node) kids.push(node);
    });

    var all = lessons();
    var nav = h("div", { class: "lesson-nav" });
    if (index > 1) {
      var prev = h("button", { type: "button", text: "Previous" });
      prev.addEventListener("click", function () {
        state.id = all[index - 2].id;
        render();
        document.getElementById("main").focus();
      });
      nav.appendChild(prev);
    }
    if (index < total) {
      var next = h("button", { type: "button", text: "Next lesson" });
      next.addEventListener("click", function () {
        state.id = all[index].id;
        render();
        document.getElementById("main").focus();
      });
      nav.appendChild(next);
    }
    kids.push(nav);

    return h("div", null, kids);
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var all = lessons();
    if (!all.length) {
      mount.innerHTML = "";
      mount.appendChild(h("p", {
        class: "disclaimer",
        text: "The lesson data did not load. Check that data/lessons.js is "
            + "present next to index.html."
      }));
      return;
    }

    if (!state.id || !find(state.id)) state.id = all[0].id;
    var index = 0;
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === state.id) index = i;
    }

    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(function (id) {
        state.id = id;
        render();
        document.getElementById("main").focus();
      }),
      renderLesson(all[index], index + 1, all.length)
    ]));
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.stereochemistry = {
    label: "Stereochemistry",
    render: render,
    open: function (id) {
      state.id = id;
      root.location.hash = "#/stereochemistry";
      render();
    }
  };
})(typeof window !== "undefined" ? window : this);
