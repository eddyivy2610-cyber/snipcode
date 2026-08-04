"""
services/vnode.py
=================
Virtual UI Tree (VNode AST) Compiler Engine & Multi-Target Serializers.
  - VNode: Framework-neutral Abstract Syntax Tree for UI components
  - build_vnode_tree: Compiles Design-System IR v4.0 into a VNode AST
  - HTMLSerializer: Serializes VNode AST to clean HTML5
  - ReactSerializer: Serializes VNode AST to React JSX
  - FlutterSerializer: Serializes VNode AST to Flutter Dart Widget Tree
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from app.services.renderers.icons import resolve_icon
from app.services.renderers.base import _spacing_to_mb_class, _cls


@dataclass
class VNode:
    """Virtual UI Node (AST) representing a UI element in memory."""
    tag: str
    id: str = ""
    variant: str = ""
    props: dict[str, Any] = field(default_factory=dict)
    classes: list[str] = field(default_factory=list)
    children: list[VNode] = field(default_factory=list)
    text_content: str = ""

    def add_child(self, child: VNode) -> None:
        self.children.append(child)


def build_vnode_tree(ir: dict[str, Any]) -> list[VNode]:
    """
    Compile a Design-System IR v4.0 dictionary into a Virtual UI Tree (VNode AST).
    """
    vnode_roots = []
    for root in ir.get("components", []):
        vnode_roots.append(_ir_to_vnode(root))
    return vnode_roots


def _ir_to_vnode(comp: dict[str, Any]) -> VNode:
    """Recursively transform an IR node into a VNode AST element."""
    comp_id = comp.get("id", "node")
    c_type = comp.get("type", "")
    variant = comp.get("variant", "")

    content = comp.get("content", {})
    layout = comp.get("layout", {})
    behavior = comp.get("behavior", {})
    children = comp.get("children", [])

    spacing_val = layout.get("margin_bottom") or layout.get("spacing_after")
    mb_cls = _spacing_to_mb_class(spacing_val)

    action = behavior.get("action")
    props = {}
    if action:
        props["data-action"] = action

    if c_type == "Form":
        classes = ["card", "form-card"]
        if mb_cls:
            classes.append(mb_cls)

        form_vnode = VNode(tag="form", id=comp_id, variant=variant, props=props, classes=classes)

        title = content.get("title")
        if title:
            form_vnode.add_child(VNode(tag="h2", classes=["container-title", "mb-24"], text_content=title))

        for child in children:
            form_vnode.add_child(_ir_to_vnode(child))

        return form_vnode

    elif c_type in ("Input", "Field"):
        classes = ["form-group"]
        if mb_cls:
            classes.append(mb_cls)

        field_vnode = VNode(tag="div", id=comp_id, variant=variant, props=props, classes=classes)

        lbl = content.get("label")
        if lbl:
            field_vnode.add_child(VNode(tag="label", classes=["form-label"], text_content=lbl))

        wrapper = VNode(tag="div", classes=["input-wrapper"])
        i_type = comp.get("input_type", "text")
        pl = content.get("placeholder", "")
        wrapper.add_child(VNode(tag="input", props={"type": i_type, "placeholder": pl}, classes=["form-input"]))

        icon_name = content.get("icon") or comp.get("trailing_icon")
        icon_symbol = resolve_icon(icon_name, "👁️" if i_type == "password" else "")
        if icon_symbol:
            wrapper.add_child(VNode(tag="span", classes=["input-icon"], text_content=icon_symbol))

        field_vnode.add_child(wrapper)
        return field_vnode

    elif c_type == "Divider" or variant == "divider":
        classes = ["divider"]
        if mb_cls:
            classes.append(mb_cls)

        txt = content.get("text", "or")
        div_vnode = VNode(tag="div", id=comp_id, variant="divider", classes=classes)
        div_vnode.add_child(VNode(tag="span", text_content=txt))
        return div_vnode

    elif c_type == "InlineAction" or variant == "inline":
        classes = ["inline-action"]
        if mb_cls:
            classes.append(mb_cls)

        txt = content.get("text", "Already have an account?")
        l_txt = content.get("link_text", "Log In")

        inline_vnode = VNode(tag="p", id=comp_id, variant="inline", props=props, classes=classes, text_content=f"{txt} ")
        inline_vnode.add_child(VNode(tag="a", props={"href": "#"}, classes=["nav-link"], text_content=l_txt))
        return inline_vnode

    elif c_type == "Button":
        classes = ["btn"]
        if mb_cls:
            classes.append(mb_cls)

        txt = content.get("text", "Submit")
        icon_name = content.get("icon") or comp.get("leading_icon")
        icon_symbol = resolve_icon(icon_name, "🌐" if variant == "oauth" else "")

        btn_vnode = VNode(tag="button", id=comp_id, variant=variant, props=props, classes=classes)
        if icon_symbol:
            btn_vnode.add_child(VNode(tag="span", classes=["btn-icon"], text_content=icon_symbol))
        btn_vnode.add_child(VNode(tag="text_span", text_content=txt))
        return btn_vnode

    else:
        classes = ["text-content"]
        if mb_cls:
            classes.append(mb_cls)
        txt = content.get("text", "")
        return VNode(tag="div", id=comp_id, classes=classes, text_content=txt)


class HTMLSerializer:
    """Serializes a VNode AST tree into HTML5 markup."""

    @classmethod
    def serialize(cls, vnode: VNode, indent: int = 1) -> str:
        sp = "  " * indent
        tag = vnode.tag

        if tag == "text_span":
            return vnode.text_content

        attr_parts = []
        if vnode.id:
            attr_parts.append(f'id="{vnode.id}"')
        if vnode.classes:
            attr_parts.append(f'class="{" ".join(vnode.classes)}"')
        for k, v in vnode.props.items():
            attr_parts.append(f'{k}="{v}"')

        attr_str = f" {' '.join(attr_parts)}" if attr_parts else ""

        if tag in ("input", "img", "br", "hr"):
            return f"{sp}<{tag}{attr_str} />"

        if not vnode.children:
            return f"{sp}<{tag}{attr_str}>{vnode.text_content}</{tag}>"

        child_lines = []
        for child in vnode.children:
            if child.tag == "text_span":
                child_lines.append(child.text_content)
            else:
                child_lines.append(cls.serialize(child, indent + 1))

        if all(c.tag == "text_span" for c in vnode.children):
            children_str = "".join(child_lines)
            return f"{sp}<{tag}{attr_str}>{vnode.text_content}{children_str}</{tag}>"

        children_block = "\n".join(child_lines)
        prefix = f"{vnode.text_content}\n" if vnode.text_content else ""
        return f"{sp}<{tag}{attr_str}>\n{prefix}{children_block}\n{sp}</{tag}>"


class ReactSerializer:
    """Serializes a VNode AST tree into React JSX code."""

    @classmethod
    def serialize(cls, vnode: VNode, indent: int = 1) -> str:
        sp = "  " * indent
        tag = vnode.tag

        if tag == "text_span":
            return vnode.text_content

        attr_parts = []
        if vnode.id:
            attr_parts.append(f'id="{vnode.id}"')
        if vnode.classes:
            attr_parts.append(f'className="{" ".join(vnode.classes)}"')
        for k, v in vnode.props.items():
            k_jsx = "type" if k == "type" else k
            attr_parts.append(f'{k_jsx}="{v}"')

        attr_str = f" {' '.join(attr_parts)}" if attr_parts else ""

        if tag in ("input", "img", "br", "hr"):
            return f"{sp}<{tag}{attr_str} />"

        if not vnode.children:
            return f"{sp}<{tag}{attr_str}>{vnode.text_content}</{tag}>"

        child_lines = []
        for child in vnode.children:
            if child.tag == "text_span":
                child_lines.append(child.text_content)
            else:
                child_lines.append(cls.serialize(child, indent + 1))

        children_block = "\n".join(child_lines)
        return f"{sp}<{tag}{attr_str}>\n{children_block}\n{sp}</{tag}>"


class FlutterSerializer:
    """Serializes a VNode AST tree into Flutter Dart Widget Code."""

    @classmethod
    def serialize(cls, vnode: VNode, indent: int = 1) -> str:
        sp = "  " * indent
        tag = vnode.tag

        if tag == "form":
            child_widgets = ",\n".join(cls.serialize(c, indent + 2) for c in vnode.children)
            return f"{sp}Card(\n{sp}  child: Column(\n{sp}    children: [\n{child_widgets}\n{sp}    ],\n{sp}  ),\n{sp})"
        elif tag == "h2":
            return f'{sp}Text("{vnode.text_content}", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold))'
        elif tag == "input":
            pl = vnode.props.get("placeholder", "")
            return f'{sp}TextFormField(decoration: InputDecoration(hintText: "{pl}"))'
        elif tag == "button":
            txt = next((c.text_content for c in vnode.children if c.tag == "text_span"), vnode.text_content)
            return sp + 'ElevatedButton(onPressed: () {}, child: Text("' + str(txt) + '"))'
        else:
            if vnode.children:
                child_widgets = ",\n".join(cls.serialize(c, indent + 1) for c in vnode.children)
                return f"{sp}Container(\n{sp}  child: Column(children: [\n{child_widgets}\n{sp}  ]),\n{sp})"
            return sp + 'Text("' + str(vnode.text_content) + '")'
