"""
main.py — Regex Syntax Tree Visualizer
Runs a two-phase animated simulation:
  Phase 1: Infix → Postfix  (token-by-token, step through the shunting-yard stack)
  Phase 2: Postfix → Syntax Tree (node-by-node tree construction)
"""
import sys
import math
import copy
import pygame
from ui_theme import (BG, PANEL, BORDER, TEXT_DARK, TEXT_MID, TEXT_LIGHT,
                      ACCENT, OPERATOR, OPERAND, ACTIVE_BG, ACTIVE_BD,
                      rounded_rect, draw_shadow)
from stack_render import StackRenderer
from tree_render  import TreeRenderer

# ─────────────────────────── Constants ───────────────────────────────
W, H        = 1200, 750
FPS         = 60
STEP_DELAY  = 1.2          # seconds between auto-steps
ANIM_SPEED  = 8.0          # lerp / fade speed (higher = faster)

EXPRESSIONS = [
    "(a* | b*)+",
    "((ε | a) | b*)*",
    "(a | b)* abb (a | b)*",
    "0? (1?)? 0*",
]

# ─────────── Shunting-Yard (minimal, for animation data) ─────────────
CONCAT       = '&'
UNARY_OPS    = set('*+?')
BINARY_OPS   = {'|', '^'}
ALL_OPS      = UNARY_OPS | BINARY_OPS | {'(', ')', CONCAT}

def precedence(t):
    if t == '(':  return 1
    if t == '|':  return 2
    if t == CONCAT: return 3
    if t in UNARY_OPS: return 4
    if t == '^':  return 5
    return 0

def fmt(t):
    return '.' if t == CONCAT else t

def is_symbol(t):
    return t not in ALL_OPS or t.startswith('\\')

def tokenize(regex):
    regex = regex.replace(' ', '')
    tokens, i = [], 0
    while i < len(regex):
        if regex[i] == '\\' and i + 1 < len(regex):
            tokens.append(regex[i:i+2]); i += 2
        else:
            tokens.append(regex[i]); i += 1
    return tokens

def add_concat(tokens):
    out = []
    for idx, t in enumerate(tokens):
        out.append(t)
        if idx + 1 == len(tokens): break
        nxt = tokens[idx + 1]
        if (is_symbol(t) or t in ')' + ''.join(UNARY_OPS)) and \
           (is_symbol(nxt) or nxt == '('):
            out.append(CONCAT)
    return out

def shunting_yard_steps(regex):
    """Return list of step dicts for the animation."""
    tokens = add_concat(tokenize(regex))
    output, stack, steps = [], [], []

    def snap(action, active_idx):
        steps.append({
            'action':     action,
            'active_tok': active_idx,
            'stack':      list(stack),
            'output':     list(output),
        })

    for idx, token in enumerate(tokens):
        if token == '(':
            stack.append(token)
            snap(f"Push '(' to stack", idx)
        elif token == ')':
            while stack and stack[-1] != '(':
                popped = stack.pop()
                output.append(popped)
                snap(f"Pop '{fmt(popped)}' → output", idx)
            if stack:
                stack.pop()
                snap("Discard '('", idx)
        elif token in ALL_OPS:
            while stack and stack[-1] != '(' and \
                  precedence(stack[-1]) >= precedence(token):
                popped = stack.pop()
                output.append(popped)
                snap(f"Pop '{fmt(popped)}' → output", idx)
            stack.append(token)
            snap(f"Push '{fmt(token)}' to stack", idx)
        else:
            output.append(token)
            snap(f"'{fmt(token)}' → output", idx)

    while stack:
        popped = stack.pop()
        output.append(popped)
        snap(f"Drain: pop '{fmt(popped)}' → output", len(tokens) - 1)

    return tokens, steps

# ──────────── Build syntax tree node list from postfix ───────────────
def build_tree_steps(postfix_tokens):
    """Return list of node_list snapshots for tree animation."""
    node_id   = [0]
    node_stack = []
    all_nodes  = []
    snapshots  = []

    def new_node(val, kind, left=None, right=None):
        nid = node_id[0]; node_id[0] += 1
        n = {
            'id': nid, 'val': val, 'type': kind,
            'parent': None, 'side': None,
            'visible': True, 'alpha': 0, 'scale': 0.4,
        }
        all_nodes.append(n)
        if left:
            left['parent'] = nid; left['side'] = 'left'
        if right:
            right['parent'] = nid; right['side'] = 'right'
        return n

    def clone_node_tree(original_node):
        if original_node is None:
            return None
        orig_left = next((n for n in all_nodes if n.get('parent') == original_node['id'] and n.get('side') == 'left'), None)
        orig_right = next((n for n in all_nodes if n.get('parent') == original_node['id'] and n.get('side') == 'right'), None)
        left_clone = clone_node_tree(orig_left)
        right_clone = clone_node_tree(orig_right)
        return new_node(original_node['val'], original_node['type'], left_clone, right_clone)

    for tok in postfix_tokens:
        t = fmt(tok)
        if t in '.|*+?^':
            if t in '.|^':
                right = node_stack.pop()
                left  = node_stack.pop()
                n = new_node(t, 'operator', left, right)
            elif t == '+':
                child = node_stack.pop()
                cloned_child = clone_node_tree(child)
                star_node = new_node('*', 'operator', cloned_child)
                n = new_node('.', 'operator', child, star_node)
            elif t == '?':
                child = node_stack.pop()
                epsilon_node = new_node('ε', 'operand')
                n = new_node('|', 'operator', child, epsilon_node)
            else:  # unary *
                child = node_stack.pop()
                n = new_node(t, 'operator', child)
            node_stack.append(n)
        else:
            n = new_node(t, 'operand')
            node_stack.append(n)

        action_msg = f"Process '{t}'"
        if t == '+':
            action_msg = "Simplify '+' as r · r*"
        elif t == '?':
            action_msg = "Simplify '?' as r | ε"

        snapshots.append({
            'token':   t,
            'nodes':   copy.deepcopy(all_nodes),
            'action':  action_msg,
        })

    return snapshots


# ─────────────────────────── Main App ────────────────────────────────
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption("Regex Syntax Tree Visualizer")
        self.clock  = pygame.time.Clock()

        self.fonts = {
            'lg':   pygame.font.SysFont('segoeui',  22, bold=True),
            'md':   pygame.font.SysFont('segoeui',  17),
            'sm':   pygame.font.SysFont('segoeui',  13),
            'mono': pygame.font.SysFont('consolas', 18, bold=True),
            'hero': pygame.font.SysFont('segoeui',  26, bold=True),
        }

        self.stack_renderer = StackRenderer()
        self.tree_renderer  = TreeRenderer()

        self.expr_idx   = 0
        self._load_expression()

        # Auto-play timer
        self.auto_play  = True
        self.timer      = 0.0
        self.time       = 0.0

        # Anim state
        self.anim_vals  = {}   # node_id → {'alpha': float, 'scale': float}
        self.push_anim  = None # {'val', 'type', 't'}

    def _load_expression(self):
        expr = EXPRESSIONS[self.expr_idx]
        self.tokens, self.pf_steps = shunting_yard_steps(expr)
        postfix_out = self.pf_steps[-1]['output'] if self.pf_steps else []
        self.tree_steps = build_tree_steps(postfix_out)

        # Phase: 'postfix' or 'tree'
        self.phase      = 'postfix'
        self.step_idx   = 0
        self.anim_vals  = {}
        self.push_anim  = None

    @property
    def current_pf_step(self):
        if self.phase == 'postfix' and self.pf_steps:
            return self.pf_steps[min(self.step_idx, len(self.pf_steps)-1)]
        return self.pf_steps[-1] if self.pf_steps else None

    @property
    def current_tree_step(self):
        if self.phase == 'tree' and self.tree_steps:
            return self.tree_steps[min(self.step_idx, len(self.tree_steps)-1)]
        return None

    def advance(self):
        if self.phase == 'postfix':
            if self.step_idx < len(self.pf_steps) - 1:
                self.step_idx += 1
                # Trigger push anim if something new appeared in stack
                old = self.pf_steps[self.step_idx - 1]['stack']
                new = self.pf_steps[self.step_idx]['stack']
                if len(new) > len(old):
                    self.push_anim = {
                        'val': fmt(new[-1]),
                        'type': 'operator' if new[-1] in ALL_OPS else 'operand',
                        't': 0.0
                    }
            else:
                self.phase     = 'tree'
                self.step_idx  = 0
        else:
            if self.step_idx < len(self.tree_steps) - 1:
                self.step_idx += 1
                # start fade-in for newly added nodes
                self._init_new_node_anims()

    def _init_new_node_anims(self):
        step = self.current_tree_step
        if step:
            for n in step['nodes']:
                if n['id'] not in self.anim_vals:
                    self.anim_vals[n['id']] = {'alpha': 0.0, 'scale': 0.4}

    def retreat(self):
        if self.phase == 'tree' and self.step_idx == 0:
            self.phase = 'postfix'
            self.step_idx = len(self.pf_steps) - 1
        elif self.step_idx > 0:
            self.step_idx -= 1

    def update(self, dt):
        self.time  += dt
        self.timer += dt

        # Push animation
        if self.push_anim is not None:
            self.push_anim['t'] = min(1.0, self.push_anim['t'] + dt * ANIM_SPEED)
            if self.push_anim['t'] >= 1.0:
                self.push_anim = None

        # Tree node fade-in
        if self.phase == 'tree':
            step = self.current_tree_step
            if step:
                for n in step['nodes']:
                    nid = n['id']
                    if nid not in self.anim_vals:
                        self.anim_vals[nid] = {'alpha': 0.0, 'scale': 0.4}
                    av = self.anim_vals[nid]
                    av['alpha'] = min(255.0, av['alpha'] + dt * ANIM_SPEED * 255)
                    av['scale'] = min(1.0,   av['scale'] + dt * ANIM_SPEED * 0.6)

        # Auto-advance
        if self.auto_play and self.timer >= STEP_DELAY:
            self.timer = 0.0
            if self.phase == 'postfix':
                self.advance()
            elif self.step_idx < len(self.tree_steps) - 1:
                self.advance()
                self._init_new_node_anims()

    def _w(self): return self.screen.get_width()
    def _h(self): return self.screen.get_height()

    def draw_rounded_panel(self, rect, title=None):
        draw_shadow(self.screen, rect)
        rounded_rect(self.screen, PANEL, rect, radius=12)
        rounded_rect(self.screen, rect, rect, radius=12, border=1, border_color=BORDER)
        if title:
            lbl = self.fonts['sm'].render(title, True, TEXT_MID)
            self.screen.blit(lbl, (rect.x + 14, rect.y + 10))

    def draw_button(self, rect, text, active=False):
        bg  = ACCENT if active else PANEL
        col = (255, 255, 255) if active else TEXT_MID
        rounded_rect(self.screen, bg, rect, radius=8)
        rounded_rect(self.screen, rect, rect, radius=8, border=1,
                     border_color=ACCENT if active else BORDER)
        t = self.fonts['sm'].render(text, True, col)
        self.screen.blit(t, t.get_rect(center=rect.center))

    def draw_header(self):
        hdr = pygame.Rect(0, 0, self._w(), 60)
        pygame.draw.rect(self.screen, PANEL, hdr)
        pygame.draw.line(self.screen, BORDER, (0, 60), (self._w(), 60), 1)
        title = self.fonts['hero'].render("Regex Syntax Tree Visualizer", True, TEXT_DARK)
        sub   = self.fonts['sm'].render("Infix → Postfix → Syntax Tree", True, TEXT_MID)
        self.screen.blit(title, (24, 12))
        self.screen.blit(sub,   (24, 42))
        ind = self.fonts['md'].render(f"Expression {self.expr_idx + 1} of {len(EXPRESSIONS)}", True, TEXT_MID)
        self.screen.blit(ind, (self._w() - ind.get_width() - 24, 22))

    def draw_expression_panel(self):
        r = pygame.Rect(24, 72, self._w() - 48, 56)
        self.draw_rounded_panel(r, "Regular Expression")
        expr = self.fonts['lg'].render(EXPRESSIONS[self.expr_idx], True, TEXT_DARK)
        self.screen.blit(expr, expr.get_rect(center=(self._w()//2, r.y + 34)))
        self.draw_button(pygame.Rect(r.x + 8, r.y + 16, 80, 26), "< Prev")
        self.draw_button(pygame.Rect(r.right - 88, r.y + 16, 80, 26), "Next >")

    def draw_conversion_panel(self):
        r = pygame.Rect(24, 138, self._w() - 48, 105)
        self.draw_rounded_panel(r, "Infix → Postfix")
        pf  = self.current_pf_step
        mid = r.x + r.width // 2
        pygame.draw.line(self.screen, BORDER, (mid, r.y + 18), (mid, r.bottom - 10), 1)
        infix_lbl = self.fonts['sm'].render("INFIX", True, TEXT_MID)
        self.screen.blit(infix_lbl, (r.x + 16, r.y + 22))
        active_idx = pf['active_tok'] if pf else -1
        tok_w, tok_h = 32, 32
        spacing = 38
        n_tokens = len(self.tokens)
        total_w = n_tokens * spacing
        start_x = r.x + 16 + (mid - r.x - 16 - total_w) // 2
        for i, t in enumerate(self.tokens):
            tr = pygame.Rect(start_x + i * spacing, r.y + 48, tok_w, tok_h)
            is_active = (i == active_idx)
            is_processed = pf and i < active_idx
            bg  = ACTIVE_BG if is_active else ((245,248,253) if is_processed else PANEL)
            bd  = ACTIVE_BD if is_active else (BORDER if not is_processed else (200,210,230))
            col = OPERATOR  if fmt(t) in '.*|+?^()' else OPERAND
            rounded_rect(self.screen, bg,  tr, radius=6)
            rounded_rect(self.screen, tr,  tr, radius=6, border=2 if is_active else 1, border_color=bd)
            if is_active:
                pulse = (math.sin(self.time * 6) + 1) / 2
                glow_r = tr.inflate(int(pulse * 6), int(pulse * 6))
                pulse_col = (*ACCENT, int(pulse * 80))
                s = pygame.Surface(glow_r.size, pygame.SRCALPHA)
                pygame.draw.rect(s, pulse_col, s.get_rect(), border_radius=8)
                self.screen.blit(s, glow_r.topleft)
                rounded_rect(self.screen, bg, tr, radius=6)
                rounded_rect(self.screen, tr, tr, radius=6, border=2, border_color=bd)
            ts = self.fonts['mono'].render(fmt(t), True, col)
            self.screen.blit(ts, ts.get_rect(center=tr.center))
        postfix_lbl = self.fonts['sm'].render("POSTFIX", True, TEXT_MID)
        self.screen.blit(postfix_lbl, (mid + 16, r.y + 22))
        out_tokens = pf['output'] if pf else []
        start_x2   = mid + 16
        for i, t in enumerate(out_tokens):
            tr = pygame.Rect(start_x2 + i * spacing, r.y + 48, tok_w, tok_h)
            col = OPERATOR if fmt(t) in '.*|+?^' else OPERAND
            rounded_rect(self.screen, (248, 249, 252), tr, radius=6)
            rounded_rect(self.screen, tr, tr, radius=6, border=1, border_color=BORDER)
            ts = self.fonts['mono'].render(fmt(t), True, col)
            self.screen.blit(ts, ts.get_rect(center=tr.center))

    def draw_stack_panel(self):
        r = pygame.Rect(24, 252, 200, self._h() - 340)
        self.draw_rounded_panel(r, "STACK")
        pf = self.current_pf_step
        stack_raw = pf['stack'] if pf else []
        items = [(fmt(t), 'operator' if t in ALL_OPS else 'operand') for t in reversed(stack_raw)]
        self.stack_renderer.draw(self.screen, r, items, self.fonts, anim_push=self.push_anim)

    def draw_tree_panel(self):
        r = pygame.Rect(234, 252, self._w() - 258, self._h() - 340)
        self.draw_rounded_panel(r, "SYNTAX TREE")
        badge_txt = self.fonts['sm'].render("Current Tree", True, ACCENT)
        self.screen.blit(badge_txt, (r.right - badge_txt.get_width() - 14, r.y + 10))
        step = self.current_tree_step
        if self.phase == 'postfix':
            msg = self.fonts['md'].render("Postfix step — tree builds next ↓", True, TEXT_LIGHT)
            self.screen.blit(msg, msg.get_rect(center=r.center))
            return
        if step:
            nodes = copy.deepcopy(step['nodes'])
            for n in nodes:
                av = self.anim_vals.get(n['id'], {'alpha': 255, 'scale': 1.0})
                n['alpha'] = int(av['alpha'])
                n['scale'] = av['scale']
            self.tree_renderer.draw(self.screen, r, nodes, fonts=self.fonts)

    def draw_current_action(self):
        r = pygame.Rect(24, self._h() - 82, self._w() - 48, 52)
        self.draw_rounded_panel(r, "CURRENT ACTION")
        if self.phase == 'postfix':
            pf = self.current_pf_step
            action = pf['action'] if pf else ''
            total  = len(self.pf_steps)
            idx    = self.step_idx
        else:
            ts     = self.current_tree_step
            action = ts['action'] if ts else ''
            total  = len(self.tree_steps)
            idx    = self.step_idx
        a_surf = self.fonts['md'].render(action, True, TEXT_DARK)
        self.screen.blit(a_surf, (r.x + 14, r.y + 26))
        phase_lbl = "Postfix" if self.phase == 'postfix' else "Tree"
        step_surf = self.fonts['sm'].render(f"{phase_lbl}  Step {idx + 1} / {total}", True, TEXT_MID)
        self.screen.blit(step_surf, (r.right - step_surf.get_width() - 14, r.y + 30))

    def draw_progress_bar(self):
        bar_r = pygame.Rect(24, self._h() - 112, self._w() - 48, 8)
        rounded_rect(self.screen, (230, 232, 238), bar_r, radius=4)
        if self.phase == 'postfix':
            prog = (self.step_idx + 1) / max(1, len(self.pf_steps))
        else:
            prog = (self.step_idx + 1) / max(1, len(self.tree_steps))
        fill_w = max(8, int(bar_r.width * prog))
        fill_r = pygame.Rect(bar_r.x, bar_r.y, fill_w, bar_r.height)
        rounded_rect(self.screen, ACCENT, fill_r, radius=4)

    def draw_controls(self):
        cy = self._h() - 28
        cx = self._w() // 2
        self.draw_button(pygame.Rect(cx - 200, cy - 16, 90, 30), "← Prev")
        self.draw_button(pygame.Rect(cx - 50,  cy - 16, 100, 30), "⏸ Pause" if self.auto_play else "▶ Play", active=self.auto_play)
        self.draw_button(pygame.Rect(cx + 60,  cy - 16, 90, 30), "Next →")
        self.draw_button(pygame.Rect(cx - 310, cy - 16, 80, 30), "↺ Restart")
        hint = self.fonts['sm'].render("← → Navigate   SPACE Play/Pause   R Restart", True, TEXT_LIGHT)
        self.screen.blit(hint, (self._w() - hint.get_width() - 24, cy - 8))
        lx = 24
        for color, label in [(OPERAND, "Operand"), (OPERATOR, "Operator"), (ACCENT, "Active Token")]:
            pygame.draw.circle(self.screen, color, (lx + 6, cy), 6)
            ls = self.fonts['sm'].render(label, True, TEXT_MID)
            self.screen.blit(ls, (lx + 16, cy - 8))
            lx += ls.get_width() + 34

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            w, h = self.screen.get_size()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.advance(); self.timer = 0
                    elif event.key == pygame.K_LEFT:
                        self.retreat(); self.timer = 0
                    elif event.key == pygame.K_SPACE:
                        self.auto_play = not self.auto_play; self.timer = 0
                    elif event.key == pygame.K_r:
                        self._load_expression()
            self.update(dt)
            self.screen.fill(BG)
            self.draw_header()
            self.draw_expression_panel()
            self.draw_conversion_panel()
            self.draw_stack_panel()
            self.draw_tree_panel()
            self.draw_progress_bar()
            self.draw_current_action()
            self.draw_controls()
            pygame.display.flip()

if __name__ == "__main__":
    App().run()
