(function () {
  "use strict";

  const BLOCK_DEFS = {
    hero: {
      label: "Hero",
      defaults: {
        headline: "New hero heading",
        subheadline: "",
        background_image_url: "",
        cta_text: "",
        cta_url: "",
        overlay_heading_level: "h1",
        overlay_font_weight: "bold",
        overlay_font_size: "2.5rem",
        overlay_font_family: "",
        overlay_text_color: "#ffffff",
        overlay_horizontal_align: "center",
        overlay_vertical_align: "center",
      },
      fields: [
        { name: "headline", label: "Headline", type: "text", required: true },
        { name: "subheadline", label: "Subheadline", type: "textarea" },
        { name: "background_image_url", label: "Background image URL", type: "url" },
        { name: "cta_text", label: "CTA text", type: "text" },
        { name: "cta_url", label: "CTA URL", type: "url" },
        { name: "overlay_heading_level", label: "Overlay heading level", type: "select", options: ["h1", "h2", "h3", "h4"] },
        { name: "overlay_font_weight", label: "Overlay font weight", type: "select", options: ["normal", "semibold", "bold", "extrabold"] },
        { name: "overlay_font_size", label: "Overlay font size", type: "text" },
        { name: "overlay_font_family", label: "Overlay font family", type: "text" },
        { name: "overlay_text_color", label: "Overlay text color", type: "color" },
        { name: "overlay_horizontal_align", label: "Overlay horizontal align", type: "select", options: ["left", "center", "right"] },
        { name: "overlay_vertical_align", label: "Overlay vertical align", type: "select", options: ["top", "center", "bottom"] },
      ],
    },
    cta_band: {
      label: "CTA band",
      defaults: {
        headline: "Act now",
        cta_text: "Learn more",
        cta_url: "",
        body: "",
        background_color: "",
        text_color: "",
      },
      fields: [
        { name: "headline", label: "Headline", type: "text", required: true },
        { name: "cta_text", label: "CTA text", type: "text", required: true },
        { name: "cta_url", label: "CTA URL", type: "url", required: true },
        { name: "body", label: "Body", type: "textarea" },
        { name: "background_color", label: "Background color", type: "color" },
        { name: "text_color", label: "Text color", type: "color" },
      ],
    },
    quote: {
      label: "Quote",
      defaults: { text: "Inspiring quote", attribution: "", source_url: "" },
      fields: [
        { name: "text", label: "Quote text", type: "textarea", required: true },
        { name: "attribution", label: "Attribution", type: "text" },
        { name: "source_url", label: "Source URL", type: "url" },
      ],
    },
    two_column: {
      label: "Two-column",
      defaults: {
        ratio: "50/50",
        gap: "2rem",
        stack_on_mobile: true,
        left_blocks: [],
        right_blocks: [],
      },
      fields: [
        { name: "ratio", label: "Ratio", type: "select", options: ["50/50", "40/60", "60/40", "67/33", "33/67"] },
        { name: "gap", label: "Gap", type: "text" },
        { name: "stack_on_mobile", label: "Stack on mobile", type: "checkbox" },
        {
          name: "left_blocks",
          label: "Left column blocks (JSON array)",
          type: "json",
          rows: 4,
        },
        {
          name: "right_blocks",
          label: "Right column blocks (JSON array)",
          type: "json",
          rows: 4,
        },
      ],
    },
    three_column: {
      label: "Three-column",
      defaults: {
        gap: "2rem",
        stack_on_mobile: true,
        col1_blocks: [],
        col2_blocks: [],
        col3_blocks: [],
      },
      fields: [
        { name: "gap", label: "Gap", type: "text" },
        { name: "stack_on_mobile", label: "Stack on mobile", type: "checkbox" },
        { name: "col1_blocks", label: "Column 1 blocks (JSON array)", type: "json", rows: 3 },
        { name: "col2_blocks", label: "Column 2 blocks (JSON array)", type: "json", rows: 3 },
        { name: "col3_blocks", label: "Column 3 blocks (JSON array)", type: "json", rows: 3 },
      ],
    },
    card: {
      label: "Card",
      defaults: { title: "Card title", body: "", image_url: "", image_alt: "", cta_text: "", cta_url: "" },
      fields: [
        { name: "title", label: "Title", type: "text", required: true },
        { name: "body", label: "Body", type: "textarea" },
        { name: "image_url", label: "Image URL", type: "url" },
        { name: "image_alt", label: "Image alt text", type: "text" },
        { name: "cta_text", label: "CTA text", type: "text" },
        { name: "cta_url", label: "CTA URL", type: "url" },
      ],
    },
    rich_text: {
      label: "Rich text",
      defaults: { body: "<p>Rich text</p>" },
      fields: [{ name: "body", label: "Rich text HTML", type: "textarea", required: true, rows: 8 }],
    },
    donation_embed: {
      label: "Donation/signup embed",
      defaults: { embed_type: "donation", embed_url: "", form_id: "", title: "", description: "" },
      fields: [
        { name: "embed_type", label: "Embed type", type: "select", options: ["donation", "signup", "email"], required: true },
        { name: "embed_url", label: "Embed URL", type: "url" },
        { name: "form_id", label: "Form ID", type: "text" },
        { name: "title", label: "Title", type: "text" },
        { name: "description", label: "Description", type: "textarea" },
      ],
    },
    alert_banner: {
      label: "Alert banner",
      defaults: { message: "Important update", level: "info", dismissible: false, cta_text: "", cta_url: "" },
      fields: [
        { name: "message", label: "Message", type: "textarea", required: true },
        { name: "level", label: "Level", type: "select", options: ["info", "warning", "success", "error"] },
        { name: "dismissible", label: "Dismissible", type: "checkbox" },
        { name: "cta_text", label: "CTA text", type: "text" },
        { name: "cta_url", label: "CTA URL", type: "url" },
      ],
    },
    faq: {
      label: "FAQ",
      defaults: { headline: "", items: [{ question: "Question?", answer: "Answer." }] },
      fields: [
        { name: "headline", label: "Headline", type: "text" },
        { name: "items", label: "FAQ items (JSON array)", type: "json", required: true, rows: 6 },
      ],
    },
  };

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  function summaryForBlock(type, props) {
    const map = {
      hero: props.headline,
      cta_band: props.headline,
      quote: props.text,
      two_column: `ratio ${props.ratio || "50/50"}`,
      three_column: `3-column${props.gap ? ` gap ${props.gap}` : ""}`,
      card: props.title,
      rich_text: (props.body || "").replace(/<[^>]*>/g, "").slice(0, 70),
      donation_embed: props.embed_type,
      alert_banner: props.message,
      faq: `${(props.items || []).length} item(s)`,
    };
    return escapeHtml(map[type] || "");
  }

  function makeCanvasMarkup(type, props) {
    const title = escapeHtml((BLOCK_DEFS[type] || {}).label || type);
    const summary = summaryForBlock(type, props);
    return `<div class="ms-builder-block" data-ms-type="${escapeHtml(type)}"><strong>${title}</strong><p>${summary}</p></div>`;
  }

  function componentForBlock(block) {
    const type = block.type;
    const props = block.props || {};
    return {
      type: "microsite-block",
      attributes: {
        "data-ms-type": type,
        "data-ms-props": JSON.stringify(props),
      },
      draggable: true,
      droppable: false,
      selectable: true,
      stylable: false,
      components: makeCanvasMarkup(type, props),
    };
  }

  function blockFromComponent(component) {
    const attrs = component.getAttributes ? component.getAttributes() : {};
    const type = attrs["data-ms-type"];
    if (!BLOCK_DEFS[type]) return null;
    let props = {};
    try {
      props = JSON.parse(attrs["data-ms-props"] || "{}");
    } catch (err) {
      props = {};
    }
    return { type, props };
  }

  function renderInspector(widgetEl, editor, component) {
    const inspector = widgetEl.querySelector("[data-builder-inspector]");
    if (!inspector) return;
    const block = blockFromComponent(component);
    if (!block) {
      inspector.innerHTML = "<p class='help'>Select a block to edit its approved settings.</p>";
      return;
    }

    const def = BLOCK_DEFS[block.type];
    const form = document.createElement("form");
    form.className = "microsite-builder-inspector-form";

    const heading = document.createElement("h4");
    heading.textContent = def.label;
    form.appendChild(heading);

    def.fields.forEach((field) => {
      const wrap = document.createElement("label");
      wrap.className = "microsite-builder-inspector-field";
      wrap.textContent = field.label;
      let input;
      if (field.type === "textarea" || field.type === "json") {
        input = document.createElement("textarea");
        input.rows = field.rows || 3;
        const value = block.props[field.name];
        input.value = field.type === "json" ? JSON.stringify(value || [], null, 2) : (value || "");
      } else if (field.type === "select") {
        input = document.createElement("select");
        (field.options || []).forEach((opt) => {
          const option = document.createElement("option");
          option.value = opt;
          option.textContent = opt;
          if ((block.props[field.name] || "") === opt) option.selected = true;
          input.appendChild(option);
        });
      } else if (field.type === "checkbox") {
        input = document.createElement("input");
        input.type = "checkbox";
        input.checked = !!block.props[field.name];
      } else {
        input = document.createElement("input");
        input.type = field.type || "text";
        input.value = block.props[field.name] || "";
      }
      input.name = field.name;
      input.dataset.fieldType = field.type || "text";
      wrap.appendChild(input);
      form.appendChild(wrap);
    });

    const save = document.createElement("button");
    save.type = "submit";
    save.textContent = "Apply settings";
    save.className = "button button-primary";
    form.appendChild(save);

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const nextProps = { ...block.props };
      const entries = form.querySelectorAll("input, textarea, select");
      for (const entry of entries) {
        const kind = entry.dataset.fieldType;
        if (kind === "checkbox") {
          nextProps[entry.name] = !!entry.checked;
        } else if (kind === "json") {
          try {
            nextProps[entry.name] = JSON.parse(entry.value || "[]");
          } catch (err) {
            window.alert(`Invalid JSON for ${entry.name}.`);
            return;
          }
        } else {
          nextProps[entry.name] = entry.value;
        }
      }
      component.setAttributes({
        ...component.getAttributes(),
        "data-ms-props": JSON.stringify(nextProps),
      });
      component.components(makeCanvasMarkup(block.type, nextProps));
      syncTextarea(widgetEl, editor);
    });

    inspector.innerHTML = "";
    inspector.appendChild(form);
  }

  function syncTextarea(widgetEl, editor) {
    const textarea = widgetEl.querySelector("textarea[name]");
    if (!textarea) return;
    const blocks = editor
      .getWrapper()
      .components()
      .map((component) => blockFromComponent(component))
      .filter(Boolean);
    textarea.value = JSON.stringify({ version: 1, blocks }, null, 2);
  }

  function loadFromTextarea(editor, textarea) {
    const raw = textarea.value && textarea.value.trim() ? textarea.value : '{"version":1,"blocks":[]}';
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (err) {
      payload = { version: 1, blocks: [] };
    }
    const blocks = Array.isArray(payload.blocks) ? payload.blocks : [];
    editor.setComponents(blocks.map((block) => componentForBlock(block)));
  }

  function initWidget(widgetEl) {
    if (widgetEl.dataset.builderInitialized === "1") return;
    widgetEl.dataset.builderInitialized = "1";
    const canvas = widgetEl.querySelector("[data-builder-canvas]");
    const palette = widgetEl.querySelector("[data-builder-palette]");
    const layers = widgetEl.querySelector("[data-builder-layers]");
    const textarea = widgetEl.querySelector("textarea[name]");
    if (!canvas || !palette || !layers || !textarea || typeof grapesjs === "undefined") return;

    const editor = grapesjs.init({
      container: canvas,
      height: "520px",
      storageManager: false,
      selectorManager: { componentFirst: true },
      styleManager: false,
      traitManager: false,
      panels: { defaults: [] },
      blockManager: { appendTo: palette },
      layerManager: { appendTo: layers },
      fromElement: false,
      components: [],
    });

    editor.DomComponents.addType("microsite-block", {
      model: {
        defaults: {
          tagName: "section",
          draggable: true,
          droppable: false,
          editable: false,
          stylable: false,
          copyable: true,
          removable: true,
        },
      },
    });

    Object.entries(BLOCK_DEFS).forEach(([type, def]) => {
      editor.BlockManager.add(`block-${type}`, {
        label: def.label,
        category: "Approved blocks",
        content: componentForBlock({ type, props: def.defaults }),
      });
    });

    loadFromTextarea(editor, textarea);
    syncTextarea(widgetEl, editor);

    editor.on("component:add", () => syncTextarea(widgetEl, editor));
    editor.on("component:remove", () => syncTextarea(widgetEl, editor));
    editor.on("component:drag:end", () => syncTextarea(widgetEl, editor));
    editor.on("component:selected", (component) => renderInspector(widgetEl, editor, component));
    editor.on("component:deselected", () => renderInspector(widgetEl, editor, null));

    const form = widgetEl.closest("form");
    if (form) {
      form.addEventListener("submit", () => syncTextarea(widgetEl, editor));
    }
  }

  function initAll() {
    const widgets = document.querySelectorAll("[data-builder-widget]");
    widgets.forEach(initWidget);
  }

  document.addEventListener("DOMContentLoaded", initAll);
  document.addEventListener("wagtail:ready", initAll);
})();
