import tkinter as tk
import math
from game_engine import RicochetGame, CellType, Direction, Position
from puzzle_generator import PuzzleGenerator

class RicochetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ricochet Robots")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        
        # Modern color palette
        self.colors = {
            'bg': '#0a0e1a',           # Deep dark blue
            'surface': '#1a1f2e',      # Dark blue-gray
            'card': '#242936',         # Lighter surface
            'primary': '#4f46e5',      # Indigo
            'secondary': '#06b6d4',    # Cyan
            'success': '#10b981',      # Emerald
            'warning': '#f59e0b',      # Amber
            'danger': '#ef4444',       # Red
            'text': '#f1f5f9',        # Light gray
            'text_muted': '#94a3b8',   # Muted gray
            'accent': '#8b5cf6',       # Purple
            'border': '#374151',       # Border gray
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Game instance
        self.game = RicochetGame()
        
        # Animation variables
        self.cell_size = 90
        self.wall_thickness = 4
        self.is_animating = False
        self.animation_speed = 8  # pixels per frame
        
        # UI state
        self.show_win_overlay = False
        
        self.setup_ui()
        self.setup_keyboard_bindings()
        self.new_game()
    
    def setup_ui(self):
        # Main container with two panels
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Game board
        self.board_frame = tk.Frame(main_frame, bg=self.colors['surface'], relief='flat', bd=0)
        self.board_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Game board canvas
        canvas_size = self.cell_size * 5 + 80
        self.canvas = tk.Canvas(
            self.board_frame,
            width=canvas_size,
            height=canvas_size,
            bg='#f8fafc',
            highlightthickness=0,
            relief='flat'
        )
        self.canvas.pack(padx=30, pady=30)
        
        # Right panel - Control dashboard
        self.control_panel = tk.Frame(main_frame, bg=self.colors['surface'], width=350)
        self.control_panel.pack(side='right', fill='y', padx=(15, 0))
        self.control_panel.pack_propagate(False)
        
        self.setup_control_panel()
    
    def setup_control_panel(self):
        # Title section
        title_frame = tk.Frame(self.control_panel, bg=self.colors['surface'])
        title_frame.pack(fill='x', padx=25, pady=(30, 20))
        
        title_label = tk.Label(
            title_frame,
            text="RICOCHET ROBOTS",
            font=('Inter', 24, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['surface']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Strategic Sliding Puzzle",
            font=('Inter', 12, 'normal'),
            fg=self.colors['text_muted'],
            bg=self.colors['surface']
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Game description
        desc_frame = tk.Frame(self.control_panel, bg=self.colors['card'])
        desc_frame.pack(fill='x', padx=25, pady=(0, 25))
        
        desc_text = """OBJECTIVE: Guide your robot to the red goal by collecting both crystals first.

MOVEMENT: Use arrow keys or WASD. Your robot slides in straight lines until it hits a wall - just like a chess rook. You cannot stop mid-slide.

STRATEGY: Plan your ricochets carefully to visit both crystal friends before reaching the goal."""
        
        desc_label = tk.Label(
            desc_frame,
            text=desc_text,
            font=('Inter', 10, 'normal'),
            fg=self.colors['text_muted'],
            bg=self.colors['card'],
            wraplength=290,
            justify='left'
        )
        desc_label.pack(padx=20, pady=15)
        
        # Status dashboard
        status_frame = tk.Frame(self.control_panel, bg=self.colors['surface'])
        status_frame.pack(fill='x', padx=25, pady=(0, 25))
        
        # Puzzle name
        puzzle_label = tk.Label(
            status_frame,
            text="PUZZLE",
            font=('Inter', 10, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['surface']
        )
        puzzle_label.pack(anchor='w')
        
        self.puzzle_name_label = tk.Label(
            status_frame,
            text="The Crossroads",
            font=('Inter', 16, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['surface']
        )
        self.puzzle_name_label.pack(anchor='w', pady=(2, 15))
        
        # Moves counter
        moves_label = tk.Label(
            status_frame,
            text="MOVES",
            font=('Inter', 10, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['surface']
        )
        moves_label.pack(anchor='w')
        
        self.moves_count_label = tk.Label(
            status_frame,
            text="0",
            font=('Inter', 24, 'bold'),
            fg=self.colors['secondary'],
            bg=self.colors['surface']
        )
        self.moves_count_label.pack(anchor='w', pady=(2, 15))
        
        # Friends progress
        friends_label = tk.Label(
            status_frame,
            text="CRYSTALS COLLECTED",
            font=('Inter', 10, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['surface']
        )
        friends_label.pack(anchor='w')
        
        progress_frame = tk.Frame(status_frame, bg=self.colors['surface'])
        progress_frame.pack(anchor='w', pady=(5, 0))
        
        self.crystal1_indicator = tk.Label(
            progress_frame,
            text="▲",
            font=('Inter', 20, 'bold'),
            fg=self.colors['border'],
            bg=self.colors['surface']
        )
        self.crystal1_indicator.pack(side='left', padx=(0, 10))
        
        self.crystal2_indicator = tk.Label(
            progress_frame,
            text="▼",
            font=('Inter', 20, 'bold'),
            fg=self.colors['border'],
            bg=self.colors['surface']
        )
        self.crystal2_indicator.pack(side='left')
        
        # Control buttons
        button_frame = tk.Frame(self.control_panel, bg=self.colors['surface'])
        button_frame.pack(fill='x', padx=25, pady=(30, 0))
        
        self.new_game_btn = tk.Button(
            button_frame,
            text="New Puzzle",
            font=('Inter', 12, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            relief='flat',
            padx=25,
            pady=12,
            cursor='hand2',
            command=self.new_game,
            bd=0
        )
        self.new_game_btn.pack(fill='x', pady=(0, 10))
        
        self.reset_btn = tk.Button(
            button_frame,
            text="Reset Position",
            font=('Inter', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            relief='flat',
            padx=25,
            pady=12,
            cursor='hand2',
            command=self.reset_position,
            bd=0
        )
        self.reset_btn.pack(fill='x')
        
        # Setup button hover effects
        self.setup_button_effects()
        
        # Legend
        legend_frame = tk.Frame(self.control_panel, bg=self.colors['surface'])
        legend_frame.pack(fill='x', padx=25, pady=(40, 0))
        
        legend_title = tk.Label(
            legend_frame,
            text="LEGEND",
            font=('Inter', 10, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['surface']
        )
        legend_title.pack(anchor='w', pady=(0, 10))
        
        legend_items = [
            ("●", self.colors['secondary'], "Robot (You)"),
            ("◆", self.colors['danger'], "Goal"),
            ("▲", self.colors['warning'], "Amber Crystal"),
            ("▼", self.colors['accent'], "Violet Crystal"),
            ("━", self.colors['text_muted'], "Walls"),
        ]
        
        for symbol, color, desc in legend_items:
            item_frame = tk.Frame(legend_frame, bg=self.colors['surface'])
            item_frame.pack(fill='x', pady=2)
            
            symbol_label = tk.Label(
                item_frame,
                text=symbol,
                font=('Inter', 14, 'bold'),
                fg=color,
                bg=self.colors['surface'],
                width=3
            )
            symbol_label.pack(side='left')
            
            desc_label = tk.Label(
                item_frame,
                text=desc,
                font=('Inter', 10, 'normal'),
                fg=self.colors['text_muted'],
                bg=self.colors['surface']
            )
            desc_label.pack(side='left', padx=(10, 0))
    
    def setup_button_effects(self):
        def on_enter_primary(e):
            self.new_game_btn.config(bg='#6366f1')
        
        def on_leave_primary(e):
            self.new_game_btn.config(bg=self.colors['primary'])
        
        def on_enter_secondary(e):
            self.reset_btn.config(bg='#374151')
        
        def on_leave_secondary(e):
            self.reset_btn.config(bg=self.colors['card'])
        
        self.new_game_btn.bind("<Enter>", on_enter_primary)
        self.new_game_btn.bind("<Leave>", on_leave_primary)
        self.reset_btn.bind("<Enter>", on_enter_secondary)
        self.reset_btn.bind("<Leave>", on_leave_secondary)
    
    def setup_keyboard_bindings(self):
        self.root.focus_set()
        
        self.root.bind('<Up>', lambda e: self.move_robot(Direction.NORTH))
        self.root.bind('<Down>', lambda e: self.move_robot(Direction.SOUTH))
        self.root.bind('<Left>', lambda e: self.move_robot(Direction.WEST))
        self.root.bind('<Right>', lambda e: self.move_robot(Direction.EAST))
        
        self.root.bind('<w>', lambda e: self.move_robot(Direction.NORTH))
        self.root.bind('<s>', lambda e: self.move_robot(Direction.SOUTH))
        self.root.bind('<a>', lambda e: self.move_robot(Direction.WEST))
        self.root.bind('<d>', lambda e: self.move_robot(Direction.EAST))
        
        self.root.bind('<space>', lambda e: self.new_game())
        self.root.bind('<r>', lambda e: self.reset_position())
    
    def move_robot(self, direction: Direction):
        if self.is_animating or self.show_win_overlay:
            return
        
        result = self.game.move_robot(direction)
        if result:
            moved, old_pos, new_pos, friend_visited = result
            if moved:
                self.animate_robot_movement(old_pos, new_pos, friend_visited)
    
    def animate_robot_movement(self, start_pos, end_pos, friend_visited=False):
        self.is_animating = True
        
        # Calculate pixel positions
        start_x = start_pos.col * self.cell_size + 40 + self.cell_size // 2
        start_y = start_pos.row * self.cell_size + 40 + self.cell_size // 2
        end_x = end_pos.col * self.cell_size + 40 + self.cell_size // 2
        end_y = end_pos.row * self.cell_size + 40 + self.cell_size // 2
        
        # Calculate movement vector
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            self.is_animating = False
            return
        
        # Normalize direction
        steps = int(distance / self.animation_speed)
        if steps == 0:
            steps = 1
            
        step_x = dx / steps
        step_y = dy / steps
        
        # Remove robot from static grid temporarily
        temp_robot_pos = self.game.robot_pos
        self.game.robot_pos = None
        self.draw_board_static()
        self.game.robot_pos = temp_robot_pos
        
        # Create animated robot
        robot_id = self.canvas.create_oval(
            start_x - 25, start_y - 25, start_x + 25, start_y + 25,
            fill=self.colors['secondary'], outline='#0891b2', width=3
        )
        
        def animate_step(step):
            if step <= steps:
                current_x = start_x + step_x * step
                current_y = start_y + step_y * step
                
                self.canvas.coords(
                    robot_id,
                    current_x - 25, current_y - 25,
                    current_x + 25, current_y + 25
                )
                
                self.root.after(20, lambda: animate_step(step + 1))
            else:
                self.canvas.delete(robot_id)
                self.draw_board()
                self.update_status()
                
                if friend_visited:
                    self.show_crystal_effect(end_pos)
                
                if self.game.game_won:
                    self.root.after(500, self.show_win_screen)
                
                self.is_animating = False
        
        animate_step(0)
    
    def show_crystal_effect(self, pos):
        # Brief ripple effect when collecting crystal
        center_x = pos.col * self.cell_size + 40 + self.cell_size // 2
        center_y = pos.row * self.cell_size + 40 + self.cell_size // 2
        
        effect_id = self.canvas.create_oval(
            center_x - 10, center_y - 10, center_x + 10, center_y + 10,
            fill='', outline=self.colors['success'], width=3
        )
        
        def expand_effect(size):
            if size < 40:
                self.canvas.coords(
                    effect_id,
                    center_x - size, center_y - size,
                    center_x + size, center_y + size
                )
                self.root.after(30, lambda: expand_effect(size + 5))
            else:
                self.canvas.delete(effect_id)
        
        expand_effect(10)
    
    def show_win_screen(self):
        self.show_win_overlay = True
        
        # Dim the board
        overlay = self.canvas.create_rectangle(
            0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
            fill='black', stipple='gray50'
        )
        
        # Win message
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        
        # Background panel
        panel = self.canvas.create_rectangle(
            center_x - 150, center_y - 80,
            center_x + 150, center_y + 80,
            fill=self.colors['surface'], outline=self.colors['primary'], width=2
        )
        
        # Win text
        win_text = self.canvas.create_text(
            center_x, center_y - 40,
            text="PUZZLE SOLVED!",
            font=('Inter', 18, 'bold'),
            fill=self.colors['text']
        )
        
        moves_text = self.canvas.create_text(
            center_x, center_y - 10,
            text=f"Completed in {self.game.move_count} moves",
            font=('Inter', 12, 'normal'),
            fill=self.colors['text_muted']
        )
        
        # Continue button
        continue_btn = self.canvas.create_rectangle(
            center_x - 80, center_y + 15,
            center_x + 80, center_y + 45,
            fill=self.colors['primary'], outline='', width=0
        )
        
        continue_text = self.canvas.create_text(
            center_x, center_y + 30,
            text="Next Puzzle",
            font=('Inter', 12, 'bold'),
            fill='white'
        )
        
        def on_continue_click(event):
            self.show_win_overlay = False
            self.new_game()
        
        self.canvas.tag_bind(continue_btn, '<Button-1>', on_continue_click)
        self.canvas.tag_bind(continue_text, '<Button-1>', on_continue_click)
        
        self.canvas.config(cursor='hand2')
        
        def reset_cursor(event):
            self.canvas.config(cursor='')
        
        self.canvas.bind('<Motion>', lambda e: self.canvas.config(cursor='hand2') 
                        if self.canvas.find_closest(e.x, e.y)[0] in [continue_btn, continue_text] 
                        else self.canvas.config(cursor=''))
    
    def new_game(self):
        self.show_win_overlay = False
        PuzzleGenerator.generate_guaranteed_solvable_puzzle(self.game)
        self.draw_board_with_fade_in()
        self.update_status()
        self.root.focus_set()
    
    def draw_board_with_fade_in(self):
        # Simple fade-in effect by drawing board normally
        # In a more advanced implementation, you could animate opacity
        self.draw_board()
    
    def reset_position(self):
        if not self.game.game_won and not self.show_win_overlay:
            self.game.robot_pos = self.game.start_pos
            self.game.visited_friends = set()
            self.game.move_count = 0
            self.game.update_grid()
            self.draw_board()
            self.update_status()
            self.root.focus_set()
    
    def update_status(self):
        # Update puzzle name
        self.puzzle_name_label.config(text=self.game.get_current_puzzle_name())
        
        # Update moves
        self.moves_count_label.config(text=str(self.game.move_count))
        
        # Update crystal indicators
        friends_visited = len(self.game.visited_friends)
        
        if self.game.friend1_pos in self.game.visited_friends:
            self.crystal1_indicator.config(fg=self.colors['warning'])
        else:
            self.crystal1_indicator.config(fg=self.colors['border'])
        
        if self.game.friend2_pos in self.game.visited_friends:
            self.crystal2_indicator.config(fg=self.colors['accent'])
        else:
            self.crystal2_indicator.config(fg=self.colors['border'])
    
    def draw_board(self):
        self.canvas.delete("all")
        self.draw_board_static()
    
    def draw_board_static(self):
        # Draw grid background with gradients
        for i in range(5):
            for j in range(5):
                x1 = j * self.cell_size + 40
                y1 = i * self.cell_size + 40
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Base cell color
                if (i + j) % 2 == 0:
                    fill_color = '#ffffff'
                    border_color = '#e5e7eb'
                else:
                    fill_color = '#f9fafb'
                    border_color = '#d1d5db'
                
                # Highlight visited friends
                if Position(i, j) in self.game.visited_friends:
                    fill_color = '#ecfdf5'
                    border_color = '#10b981'
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill_color, outline=border_color, width=1
                )
                
                # Draw cell content
                cell_type = self.game.grid[i][j]
                center_x = x1 + self.cell_size // 2
                center_y = y1 + self.cell_size // 2
                
                if cell_type == CellType.ROBOT:
                    # Robot - sleek cyan circle
                    self.canvas.create_oval(
                        x1 + 15, y1 + 15, x2 - 15, y2 - 15,
                        fill=self.colors['secondary'], outline='#0891b2', width=3
                    )
                    # Inner glow effect
                    self.canvas.create_oval(
                        center_x - 8, center_y - 8, center_x + 8, center_y + 8,
                        fill='white', outline=''
                    )
                
                elif cell_type == CellType.START:
                    # Start position marker
                    self.canvas.create_rectangle(
                        x1 + 25, y1 + 25, x2 - 25, y2 - 25,
                        fill='#dcfce7', outline=self.colors['success'], width=2
                    )
                    self.canvas.create_text(
                        center_x, center_y,
                        text="START", font=('Inter', 8, 'bold'),
                        fill=self.colors['success']
                    )
                
                elif cell_type == CellType.GOAL:
                    # Goal - radiant gem
                    # Outer diamond
                    points = [
                        center_x, y1 + 15,
                        x2 - 15, center_y,
                        center_x, y2 - 15,
                        x1 + 15, center_y
                    ]
                    self.canvas.create_polygon(
                        points, fill=self.colors['danger'], outline='#991b1b', width=2
                    )
                    # Inner shine
                    inner_points = [
                        center_x, y1 + 25,
                        x2 - 25, center_y,
                        center_x, y2 - 25,
                        x1 + 25, center_y
                    ]
                    self.canvas.create_polygon(
                        inner_points, fill='#fca5a5', outline=''
                    )
                
                elif cell_type == CellType.FRIEND1:
                    # Amber crystal
                    points = [
                        center_x, y1 + 15,
                        x2 - 15, y2 - 15,
                        x1 + 15, y2 - 15
                    ]
                    self.canvas.create_polygon(
                        points, fill=self.colors['warning'], outline='#d97706', width=2
                    )
                    # Crystal shine
                    shine_points = [
                        center_x, y1 + 25,
                        x2 - 25, y2 - 25,
                        x1 + 25, y2 - 25
                    ]
                    self.canvas.create_polygon(
                        shine_points, fill='#fcd34d', outline=''
                    )
                
                elif cell_type == CellType.FRIEND2:
                    # Violet crystal
                    points = [
                        x1 + 15, y1 + 15,
                        x2 - 15, y1 + 15,
                        center_x, y2 - 15
                    ]
                    self.canvas.create_polygon(
                        points, fill=self.colors['accent'], outline='#7c3aed', width=2
                    )
                    # Crystal shine
                    shine_points = [
                        x1 + 25, y1 + 25,
                        x2 - 25, y1 + 25,
                        center_x, y2 - 25
                    ]
                    self.canvas.create_polygon(
                        shine_points, fill='#c4b5fd', outline=''
                    )
        
        # Draw walls with 3D effect
        self.draw_walls()
    
    def draw_walls(self):
        for wall in self.game.walls:
            a, b = wall.from_pos, wall.to_pos
            valid_a = self.game.is_valid_position(a)
            valid_b = self.game.is_valid_position(b)
            if valid_a and valid_b:
                from_x = a.col * self.cell_size + 40
                from_y = a.row * self.cell_size + 40
                to_x = b.col * self.cell_size + 40
                to_y = b.row * self.cell_size + 40
                # Vertical wall
                if a.row == b.row:
                    wall_x = max(from_x, to_x)
                    wall_y1 = from_y + 8
                    wall_y2 = from_y + self.cell_size - 8
                    self.canvas.create_line(
                        wall_x, wall_y1, wall_x, wall_y2,
                        fill='#374151', width=self.wall_thickness, capstyle='round', joinstyle='round'
                    )
                    self.canvas.create_line(
                        wall_x - 1, wall_y1, wall_x - 1, wall_y2,
                        fill='#6b7280', width=1, capstyle='round', joinstyle='round'
                    )
                # Horizontal wall
                elif a.col == b.col:
                    wall_y = max(from_y, to_y)
                    wall_x1 = from_x + 8
                    wall_x2 = from_x + self.cell_size - 8
                    self.canvas.create_line(
                        wall_x1, wall_y, wall_x2, wall_y,
                        fill='#374151', width=self.wall_thickness, capstyle='round', joinstyle='round'
                    )
                    self.canvas.create_line(
                        wall_x1, wall_y - 1, wall_x2, wall_y - 1,
                        fill='#6b7280', width=1, capstyle='round', joinstyle='round'
                    )
            elif valid_a and not valid_b:
                x = a.col * self.cell_size + 40
                y = a.row * self.cell_size + 40
                # Top edge
                if a.row == 0 and b.row < 0:
                    self.canvas.create_line(
                        x, y, x + self.cell_size, y,
                        fill='#374151', width=self.wall_thickness, capstyle='round', joinstyle='round'
                    )
                # Bottom edge
                elif a.row == self.game.grid_size - 1 and b.row > a.row:
                    self.canvas.create_line(
                        x, y + self.cell_size, x + self.cell_size, y + self.cell_size,
                        fill='#374151', width=self.wall_thickness, capstyle='round', joinstyle='round'
                    )
                # Left edge
                if a.col == 0 and b.col < 0:
                    self.canvas.create_line(
                        x, y, x, y + self.cell_size,
                        fill='#374151', width=self.wall_thickness, capstyle='round', joinstyle='round'
                    )
                # Right edge
                elif a.col == self.game.grid_size - 1 and b.col > a.col:
                    self.canvas.create_line(
                        x + self.cell_size, y, x + self.cell_size, y + self.cell_size,
                        fill='#374151', width=self.wall_thickness, capstyle='round', joinstyle='round'
                    )

def main():
    root = tk.Tk()
    RicochetGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()