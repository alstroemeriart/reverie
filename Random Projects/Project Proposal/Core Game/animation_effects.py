"""
animation_effects.py — Reusable animation system for Game-On Learning.
Provides floating text, screen shakes, color flashes, and particle effects.
"""

import tkinter as tk
import math
import time
from typing import Optional, Callable, Any


class FloatingText:
    """Animated text that floats up and fades out."""
    
    def __init__(self, canvas: tk.Canvas, x: float, y: float, text: str,
                 color: str, font_size: int = 14, duration: float = 1.5,
                 speed: float = 30):
        self.canvas = canvas
        self.start_x = x
        self.start_y = y
        self.text = text
        self.color = color
        self.font_size = font_size
        self.duration = duration
        self.speed = speed
        self.start_time = time.time()
        self.text_id: Optional[int] = None
        self.is_alive = True
    
    def update(self) -> bool:
        """Update animation. Returns True if still alive, False if done."""
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            self.is_alive = False
            if self.text_id:
                self.canvas.delete(self.text_id)
            return False
        
        # Move up
        y = self.start_y - progress * self.speed
        
        # Fade out
        alpha = int(255 * (1 - progress))
        # Convert alpha to a fade effect by adjusting color brightness
        faded_color = self._fade_color(self.color, alpha)
        
        if self.text_id:
            self.canvas.delete(self.text_id)
        
        self.text_id = self.canvas.create_text(
            self.start_x, y, text=self.text,
            fill=faded_color,
            font=("Courier New", self.font_size, "bold"),
            justify="center"
        )
        
        return True
    
    @staticmethod
    def _fade_color(hex_color: str, alpha: int) -> str:
        """Blend hex color towards background."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Background is dark (#0d1117), so blend towards that
        bg_r, bg_g, bg_b = 0x0d, 0x11, 0x17
        alpha_f = alpha / 255.0
        
        r = int(r * alpha_f + bg_r * (1 - alpha_f))
        g = int(g * alpha_f + bg_g * (1 - alpha_f))
        b = int(b * alpha_f + bg_b * (1 - alpha_f))
        
        return f"#{r:02x}{g:02x}{b:02x}"


class ScreenShake:
    """Temporary screen shake effect."""
    
    def __init__(self, canvas: tk.Canvas, intensity: float = 5,
                 duration: float = 0.3, frequency: float = 15):
        self.canvas = canvas
        self.intensity = intensity
        self.duration = duration
        self.frequency = frequency
        self.start_time = time.time()
        self.start_x = canvas.xview()[0] if hasattr(canvas, 'xview') else 0
        self.start_y = canvas.yview()[0] if hasattr(canvas, 'yview') else 0
        self.is_active = True
    
    def update(self) -> bool:
        """Apply shake offset. Returns True if still active."""
        elapsed = time.time() - self.start_time
        
        if elapsed >= self.duration:
            self.is_active = False
            return False
        
        # Sine wave shake that decays over time
        decay = 1 - (elapsed / self.duration)
        shake_x = math.sin(elapsed * self.frequency * math.pi) * self.intensity * decay
        shake_y = math.cos(elapsed * self.frequency * math.pi * 0.7) * self.intensity * decay * 0.5
        
        # Apply shake via canvas transform (approximate by moving content)
        # Note: Tkinter doesn't support native transforms, so this is visual feedback
        return True


class ColorFlash:
    """Temporary color overlay on a widget or canvas."""
    
    def __init__(self, canvas: tk.Canvas, color: str, duration: float = 0.2):
        self.canvas = canvas
        self.flash_color = color
        self.duration = duration
        self.start_time = time.time()
        self.overlay_id: Optional[int] = None
        self.original_bg = canvas["bg"]
        self.is_active = True
    
    def update(self) -> bool:
        """Apply color flash. Returns True if still active."""
        elapsed = time.time() - self.start_time
        
        if elapsed >= self.duration:
            self.is_active = False
            if self.overlay_id:
                self.canvas.delete(self.overlay_id)
            return False
        
        # Flash intensity fades out
        intensity = 1 - (elapsed / self.duration)
        alpha = int(150 * intensity)
        
        # Create overlay rectangle
        if self.overlay_id:
            self.canvas.delete(self.overlay_id)
        
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        
        # Blend the flash color
        blended = self._blend_color(self.flash_color, alpha)
        
        self.overlay_id = self.canvas.create_rectangle(
            0, 0, w, h,
            fill=blended, outline=""
        )
        self.canvas.tag_lower(self.overlay_id)
        
        return True
    
    @staticmethod
    def _blend_color(hex_color: str, alpha: int) -> str:
        """Blend color with transparency effect."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Keep the color but reduce saturation as alpha increases
        alpha_f = alpha / 255.0
        
        # Desaturate by moving toward gray
        gray = (r + g + b) // 3
        r = int(r * alpha_f + gray * (1 - alpha_f))
        g = int(g * alpha_f + gray * (1 - alpha_f))
        b = int(b * alpha_f + gray * (1 - alpha_f))
        
        return f"#{r:02x}{g:02x}{b:02x}"


class ParticleEmitter:
    """Emit and animate particles (simple dots)."""
    
    def __init__(self, canvas: tk.Canvas, x: float, y: float,
                 count: int = 12, color: str = "#58a6ff",
                 speed: float = 60, duration: float = 0.8):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.start_time = time.time()
        self.particles = []
        
        # Create particles at various angles
        for i in range(count):
            angle = (i / count) * 2 * math.pi
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle_id = canvas.create_oval(
                x - 2, y - 2, x + 2, y + 2,
                fill=color, outline=""
            )
            self.particles.append({
                "id": particle_id,
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy
            })
        
        self.is_alive = True
    
    def update(self) -> bool:
        """Update all particles. Returns True if still alive."""
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            self.is_alive = False
            for p in self.particles:
                self.canvas.delete(p["id"])
            return False
        
        # Update gravity and positions
        for p in self.particles:
            p["vy"] += 40 * 0.016  # gravity
            p["x"] += p["vx"] * 0.016
            p["y"] += p["vy"] * 0.016
            
            # Fade out
            faded = self._fade_color(self.color, int(255 * (1 - progress)))
            
            self.canvas.coords(p["id"],
                              p["x"] - 2, p["y"] - 2,
                              p["x"] + 2, p["y"] + 2)
            self.canvas.itemconfig(p["id"], fill=faded)
        
        return True
    
    @staticmethod
    def _fade_color(hex_color: str, alpha: int) -> str:
        """Fade color to background."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        bg_r, bg_g, bg_b = 0x0d, 0x11, 0x17
        alpha_f = alpha / 255.0
        
        r = int(r * alpha_f + bg_r * (1 - alpha_f))
        g = int(g * alpha_f + bg_g * (1 - alpha_f))
        b = int(b * alpha_f + bg_b * (1 - alpha_f))
        
        return f"#{r:02x}{g:02x}{b:02x}"


class PulseEffect:
    """Pulsing scale animation for emphasis."""
    
    def __init__(self, canvas: tk.Canvas, item_id: int, 
                 min_scale: float = 0.9, max_scale: float = 1.1,
                 duration: float = 0.4, cycles: int = 1):
        self.canvas = canvas
        self.item_id = item_id
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.duration = duration
        self.cycles = cycles
        self.start_time = time.time()
        self.is_alive = True
    
    def update(self) -> bool:
        """Update pulse animation."""
        elapsed = time.time() - self.start_time
        total_duration = self.duration * self.cycles
        
        if elapsed >= total_duration:
            self.is_alive = False
            return False
        
        # Sawtooth wave for pulsing
        cycle_progress = (elapsed % self.duration) / self.duration
        scale = self.min_scale + (self.max_scale - self.min_scale) * abs(math.sin(cycle_progress * math.pi))
        
        # Note: This is a visual effect; actual scaling would require more complex transforms
        return True


class AnimationManager:
    """Centralized manager for all active animations."""
    
    def __init__(self, canvas: tk.Canvas, update_rate: int = 16):
        self.canvas = canvas
        self.update_rate = update_rate
        self.floating_texts: list[FloatingText] = []
        self.screen_shakes: list[ScreenShake] = []
        self.color_flashes: list[ColorFlash] = []
        self.particles: list[ParticleEmitter] = []
        self.pulses: list[PulseEffect] = []
        self._update_id: Optional[str] = None
    
    def add_floating_text(self, x: float, y: float, text: str, color: str,
                         font_size: int = 14, duration: float = 1.5) -> None:
        """Add floating text animation."""
        ft = FloatingText(self.canvas, x, y, text, color, font_size, duration)
        self.floating_texts.append(ft)
    
    def add_screen_shake(self, intensity: float = 5, duration: float = 0.3) -> None:
        """Add screen shake effect."""
        ss = ScreenShake(self.canvas, intensity, duration)
        self.screen_shakes.append(ss)
    
    def add_color_flash(self, color: str, duration: float = 0.2) -> None:
        """Add color flash effect."""
        cf = ColorFlash(self.canvas, color, duration)
        self.color_flashes.append(cf)
    
    def add_particles(self, x: float, y: float, count: int = 12,
                     color: str = "#58a6ff", speed: float = 60) -> None:
        """Add particle burst effect."""
        pe = ParticleEmitter(self.canvas, x, y, count, color, speed)
        self.particles.append(pe)
    
    def add_pulse(self, item_id: int, min_scale: float = 0.9, 
                 max_scale: float = 1.1, duration: float = 0.4) -> None:
        """Add pulse effect to canvas item."""
        pulse = PulseEffect(self.canvas, item_id, min_scale, max_scale, duration)
        self.pulses.append(pulse)
    
    def start(self) -> None:
        """Start the animation loop."""
        self._update()
    
    def stop(self) -> None:
        """Stop the animation loop."""
        if self._update_id:
            self.canvas.after_cancel(self._update_id)
            self._update_id = None
    
    def _update(self) -> None:
        """Update all active animations."""
        try:
            # Update floating texts
            self.floating_texts = [ft for ft in self.floating_texts if ft.update()]
            
            # Update screen shakes
            self.screen_shakes = [ss for ss in self.screen_shakes if ss.update()]
            
            # Update color flashes
            self.color_flashes = [cf for cf in self.color_flashes if cf.update()]
            
            # Update particles
            self.particles = [pe for pe in self.particles if pe.update()]
            
            # Update pulses
            self.pulses = [p for p in self.pulses if p.update()]
        except tk.TclError:
            # Canvas was destroyed
            self.stop()
            return
        
        # Schedule next update
        self._update_id = self.canvas.after(self.update_rate, self._update)


class TextFadeTransition:
    """Fade out text, replace it, then fade back in."""
    
    def __init__(self, text_widget: tk.Text, new_content: str,
                 duration: float = 0.5):
        self.widget = text_widget
        self.new_content = new_content
        self.duration = duration
        self.start_time = time.time()
        self.halfway = False
        self.is_active = True
    
    def update(self) -> bool:
        """Update transition. Returns True if ongoing."""
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            self.is_active = False
            return False
        
        # First half: fade out
        # Second half: fade in new content
        if progress < 0.5 and not self.halfway:
            # Fading out
            self.widget.config(fg="#484f58")  # Dim text
        elif progress >= 0.5 and not self.halfway:
            # Switch content at halfway point
            self.halfway = True
            self.widget.delete("1.0", tk.END)
            self.widget.insert("1.0", self.new_content)
            self.widget.config(fg="#8b949e")  # Still dim
        
        if progress >= 1.0:
            self.widget.config(fg="#e6edf3")  # Restore normal color
        
        return True


def shake_effect(canvas: tk.Canvas, intensity: float = 8) -> None:
    """Quick shake effect helper."""
    original_x = canvas.xview()[0] if hasattr(canvas, 'xview') else 0
    original_y = canvas.yview()[0] if hasattr(canvas, 'yview') else 0
    
    def apply_shake(frame: int = 0) -> None:
        if frame < 8:
            offset = math.sin(frame * math.pi) * intensity / 100
            if hasattr(canvas, 'xview'):
                canvas.xview("moveto", original_x + offset)
            canvas.after(30, apply_shake, frame + 1)
        else:
            if hasattr(canvas, 'xview'):
                canvas.xview("moveto", original_x)
    
    apply_shake()


def flash_effect(widget: tk.Widget, color: str = "#f85149", duration: int = 200) -> None:
    """Quick flash effect helper."""
    original_bg = widget["bg"]
    
    def fade_back() -> None:
        try:
            widget.config(bg=original_bg)
        except:
            pass
    
    try:
        widget.config(bg=color)
    except:
        pass
    widget.after(duration, fade_back)


# Convenience aliases
shake = shake_effect
flash = flash_effect

