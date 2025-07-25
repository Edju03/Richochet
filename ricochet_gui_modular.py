import tkinter as tk
import math
from game_engine import RicochetGame, CellType, Direction, Position
from puzzle_generator import PuzzleGenerator

class RicochetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ricochet Robots")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.root.minsize(1200, 800)
        
        # Enhanced modern color palette
        self.colors = {
            'bg': '#0f0f23',           # Deep space blue
            'surface': '#1e1e3e',      # Rich dark purple
            'card': '#2a2a4a',         # Elevated surface
            'card_hover': '#34344e',   # Hover state
            'primary': '#6366f1',      # Modern indigo
            'primary_hover': '#7c3aed', # Primary hover
            'secondary': '#06b6d4',    # Bright cyan
            'success': '#10b981',      # Emerald
            'warning': '#f59e0b',      # Amber
            'danger': '#ef4444',       # Red
            'text': '#f8fafc',        # Pure white
            'text_secondary': '#cbd5e1', # Light gray
            'text_muted': '#64748b',   # Muted blue-gray
            'accent': '#8b5cf6',       # Purple accent
            'border': '#475569',       # Border gray
            'gradient_start': '#1e293b',
            'gradient_end': '#334155',
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Game instance
        self.game = RicochetGame()
        
        # Animation variables
        self.cell_size = 120  # Increased for larger board
        self.wall_thickness = 5
        self.is_animating = False
        self.animation_speed = 8  # pixels per frame
        
        # UI state
        self.show_win_overlay = False
        self.difficulty_var = tk.StringVar(value='Medium')
        self.last_optimal_moves = None
        
        self.setup_ui()
        self.setup_keyboard_bindings()
        self.new_game()
    
    def setup_ui(self):
        # Main container with elegant spacing
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Left panel - Game board with shadow effect
        board_container = tk.Frame(main_frame, bg=self.colors['bg'])
        board_container.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        # Board shadow frame
        shadow_frame = tk.Frame(board_container, bg='#000000', bd=0)
        shadow_frame.pack(padx=3, pady=3, anchor='nw')
        
        # Main board frame with rounded appearance
        self.board_frame = tk.Frame(shadow_frame, bg=self.colors['surface'], relief='flat', bd=2)
        self.board_frame.pack(padx=0, pady=0)
        
        # Board title
        board_title = tk.Label(
            self.board_frame,
            text="GAME BOARD",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['surface']
        )
        board_title.pack(pady=(20, 10))
        
        # Game board canvas with enhanced styling
        canvas_size = self.cell_size * 5 + 40
        self.canvas = tk.Canvas(
            self.board_frame,
            width=canvas_size,
            height=canvas_size,
            bg='#f8fafc',  # Light gray background instead of white
            highlightthickness=2,
            highlightcolor=self.colors['primary'],
            highlightbackground=self.colors['border'],
            relief='flat'
        )
        self.canvas.pack(padx=30, pady=(10, 30))
        
        # Right panel - Control dashboard with enhanced design and scrolling
        self.control_panel = tk.Frame(main_frame, bg=self.colors['surface'], width=450, relief='solid', bd=1)
        self.control_panel.pack(side='right', fill='y', padx=(20, 0))
        self.control_panel.pack_propagate(False)
        
        self.setup_control_panel()
    
    def setup_control_panel(self):
        # Header section with gradient-like effect
        header_frame = tk.Frame(self.control_panel, bg=self.colors['gradient_start'], height=120)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title with enhanced typography
        title_label = tk.Label(
            header_frame,
            text="RICOCHET",
            font=('Segoe UI', 28, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['gradient_start']
        )
        title_label.pack(pady=(25, 0))
        
        subtitle_label = tk.Label(
            header_frame,
            text="ROBOTS",
            font=('Segoe UI', 28, 'bold'),
            fg=self.colors['secondary'],
            bg=self.colors['gradient_start']
        )
        subtitle_label.pack(pady=(0, 25))
        
        # Scrollable content area with scrollbar
        canvas_frame = tk.Frame(self.control_panel, bg=self.colors['surface'])
        canvas_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Create canvas and scrollbar for scrolling
        content_canvas = tk.Canvas(canvas_frame, bg=self.colors['surface'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient='vertical', command=content_canvas.yview)
        content_frame = tk.Frame(content_canvas, bg=self.colors['surface'])
        
        content_frame.bind('<Configure>', lambda e: content_canvas.configure(scrollregion=content_canvas.bbox('all')))
        content_canvas.create_window((0, 0), window=content_frame, anchor='nw')
        content_canvas.configure(yscrollcommand=scrollbar.set)
        
        content_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        content_canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Game description in elegant card
        desc_card = tk.Frame(content_frame, bg=self.colors['card'], relief='flat', bd=1)
        desc_card.pack(fill='x', padx=20, pady=(20, 15))
        
        desc_title = tk.Label(
            desc_card,
            text="HOW TO PLAY",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card']
        )
        desc_title.pack(pady=(15, 10))
        
        # Objective section
        obj_label = tk.Label(
            desc_card,
            text="OBJECTIVE",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['warning'],
            bg=self.colors['card']
        )
        obj_label.pack(anchor='w', padx=15, pady=(5, 0))
        
        obj_text = tk.Label(
            desc_card,
            text="Collect both crystals, then reach the red goal",
            font=('Segoe UI', 9, 'normal'),
            fg=self.colors['text_secondary'],
            bg=self.colors['card'],
            wraplength=350,
            justify='left'
        )
        obj_text.pack(anchor='w', padx=15, pady=(2, 8))
        
        # Movement section
        move_label = tk.Label(
            desc_card,
            text="CONTROLS",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['secondary'],
            bg=self.colors['card']
        )
        move_label.pack(anchor='w', padx=15, pady=(0, 0))
        
        move_text = tk.Label(
            desc_card,
            text="Arrow keys or WASD • Robot slides until hitting walls",
            font=('Segoe UI', 9, 'normal'),
            fg=self.colors['text_secondary'],
            bg=self.colors['card'],
            wraplength=350,
            justify='left'
        )
        move_text.pack(anchor='w', padx=15, pady=(2, 15))
        
        # Game stats in modern cards
        stats_container = tk.Frame(content_frame, bg=self.colors['surface'])
        stats_container.pack(fill='x', padx=20, pady=(0, 15))
        
        # Stats row 1 - Difficulty only
        stats_row1 = tk.Frame(stats_container, bg=self.colors['surface'])
        stats_row1.pack(fill='x', pady=(0, 10))
        
        # Difficulty card (full width)
        diff_card = tk.Frame(stats_row1, bg=self.colors['card'], relief='flat', bd=1)
        diff_card.pack(fill='x')
        
        diff_title = tk.Label(
            diff_card,
            text="DIFFICULTY",
            font=('Segoe UI', 9, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['card']
        )
        diff_title.pack(pady=(10, 5))
        
        # Difficulty dropdown with reliable styling - neutral colors inside colored frame  
        diff_menu_frame = tk.Frame(diff_card, bg=self.colors['success'], relief='solid', bd=2)
        diff_menu_frame.pack(pady=(0, 10), padx=20)
        
        self.difficulty_var = tk.StringVar(value='Medium')
        diff_menu = tk.OptionMenu(
            diff_menu_frame,
            self.difficulty_var,
            'Easy', 'Medium', 'Hard'
        )
        diff_menu.config(
            font=('Segoe UI', 10, 'bold'),
            bg='#d1fae5',           # Light mint green background - appealing and visible
            fg='#065f46',           # Dark green text - readable and matches theme
            activebackground='#a7f3d0',  # Slightly darker mint on hover
            activeforeground='#065f46',
            relief='flat',
            bd=0,
            highlightthickness=0,
            width=12,
            cursor='hand2',
            indicatoron=0           # Hide default indicator for cleaner look
        )
        # Style the dropdown menu
        diff_menu['menu'].config(
            bg='#d1fae5',
            fg='#065f46', 
            activebackground=self.colors['success'],
            activeforeground='white',
            font=('Segoe UI', 10)
        )
        diff_menu.pack(fill='x', padx=2, pady=2)
        
        # Stats row 2 - Moves and Optimal
        stats_row2 = tk.Frame(stats_container, bg=self.colors['surface'])
        stats_row2.pack(fill='x', pady=(0, 10))
        
        # Moves card
        moves_card = tk.Frame(stats_row2, bg=self.colors['card'], relief='flat', bd=1)
        moves_card.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        moves_title = tk.Label(
            moves_card,
            text="YOUR MOVES",
            font=('Segoe UI', 9, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['card']
        )
        moves_title.pack(pady=(10, 2))
        
        self.moves_count_label = tk.Label(
            moves_card,
            text="0",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['secondary'],
            bg=self.colors['card']
        )
        self.moves_count_label.pack(pady=(0, 10))
        
        # Optimal moves card
        optimal_card = tk.Frame(stats_row2, bg=self.colors['card'], relief='flat', bd=1)
        optimal_card.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        optimal_title = tk.Label(
            optimal_card,
            text="OPTIMAL",
            font=('Segoe UI', 9, 'bold'),
            fg=self.colors['text_muted'],
            bg=self.colors['card']
        )
        optimal_title.pack(pady=(10, 2))
        
        self.optimal_moves_value = tk.Label(
            optimal_card,
            text="-",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['warning'],
            bg=self.colors['card']
        )
        self.optimal_moves_value.pack(pady=(0, 10))
        
        # Crystal progress card
        crystal_card = tk.Frame(content_frame, bg=self.colors['card'], relief='flat', bd=1)
        crystal_card.pack(fill='x', padx=20, pady=(0, 15))
        
        crystal_title = tk.Label(
            crystal_card,
            text="CRYSTAL PROGRESS",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card']
        )
        crystal_title.pack(pady=(15, 10))
        
        progress_frame = tk.Frame(crystal_card, bg=self.colors['card'])
        progress_frame.pack(pady=(0, 15))
        
        # Crystal indicators with labels
        crystal1_frame = tk.Frame(progress_frame, bg=self.colors['card'])
        crystal1_frame.pack(side='left', padx=20)
        
        crystal1_label = tk.Label(
            crystal1_frame,
            text="Amber",
            font=('Segoe UI', 8, 'normal'),
            fg=self.colors['text_muted'],
            bg=self.colors['card']
        )
        crystal1_label.pack()
        
        self.crystal1_indicator = tk.Label(
            crystal1_frame,
            text="▲",
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['border'],
            bg=self.colors['card']
        )
        self.crystal1_indicator.pack()
        
        crystal2_frame = tk.Frame(progress_frame, bg=self.colors['card'])
        crystal2_frame.pack(side='right', padx=20)
        
        crystal2_label = tk.Label(
            crystal2_frame,
            text="Violet",
            font=('Segoe UI', 8, 'normal'),
            fg=self.colors['text_muted'],
            bg=self.colors['card']
        )
        crystal2_label.pack()
        
        self.crystal2_indicator = tk.Label(
            crystal2_frame,
            text="▼",
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['border'],
            bg=self.colors['card']
        )
        self.crystal2_indicator.pack()
        
        # Action buttons with reliable styling - neutral button colors inside colored frames
        button_container = tk.Frame(content_frame, bg=self.colors['surface'])
        button_container.pack(fill='x', padx=20, pady=(0, 15))
        
        # Appealing button colors that tkinter will actually respect
        # Each button gets a subtle tinted background that matches its purpose
        button_colors = {
            'primary': {
                'bg': '#ddd6fe',        # Light lavender (matches indigo theme)
                'fg': '#3730a3',        # Deep indigo text
                'hover': '#c4b5fd'      # Slightly darker lavender on hover
            },
            'warning': {
                'bg': '#fed7aa',        # Light peach (matches orange theme)  
                'fg': '#9a3412',        # Deep orange text
                'hover': '#fdba74'      # Slightly darker peach on hover
            },
            'accent': {
                'bg': '#e9d5ff',        # Light purple (matches purple theme)
                'fg': '#6b21a8',        # Deep purple text
                'hover': '#ddd6fe'      # Slightly darker purple on hover
            }
        }
        
        # Helper function to create appealing buttons
        def create_custom_button(parent, text, command, border_color, button_type, is_last=False):
            # The outer frame provides the colored border/background
            bottom_padding = 0 if is_last else 8
            btn_frame = tk.Frame(parent, bg=border_color, relief='solid', bd=2)
            btn_frame.pack(fill='x', pady=(0, bottom_padding))
            
            # The Button uses appealing colors that complement the theme
            colors = button_colors[button_type]
            button = tk.Button(
                btn_frame,
                text=text,
                font=('Segoe UI', 11, 'bold'),
                bg=colors['bg'],             # Tinted background - visually appealing
                fg=colors['fg'],             # Matching dark text - always readable
                activebackground=colors['hover'],  # Hover state
                activeforeground=colors['fg'],
                relief='flat',
                bd=0,
                cursor='hand2',
                command=command,
                pady=10,
                highlightthickness=0
            )
            button.pack(fill='both', expand=True, padx=2, pady=2)
            return button
        
        # Create buttons with appealing colored backgrounds that match their purpose
        self.new_game_btn = create_custom_button(button_container, "NEW PUZZLE", self.new_game, self.colors['primary'], 'primary')
        self.reset_btn = create_custom_button(button_container, "RESET POSITION", self.reset_position, self.colors['warning'], 'warning')  
        self.show_solution_btn = create_custom_button(button_container, "SHOW SOLUTION", self.show_solution, self.colors['accent'], 'accent', is_last=True)
        
        # Legend section in elegant card
        legend_card = tk.Frame(content_frame, bg=self.colors['card'], relief='flat', bd=1)
        legend_card.pack(fill='x', padx=20, pady=(0, 20))
        
        legend_header = tk.Label(
            legend_card,
            text="GAME ELEMENTS",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['card']
        )
        legend_header.pack(pady=(15, 10))
        
        # Legend items in a grid
        legend_grid = tk.Frame(legend_card, bg=self.colors['card'])
        legend_grid.pack(pady=(0, 15), padx=15)
        
        legend_items = [
            ("●", self.colors['secondary'], "Your Robot"),
            ("◆", self.colors['danger'], "Goal Target"),
            ("▲", self.colors['warning'], "Amber Crystal"),
            ("▼", self.colors['accent'], "Violet Crystal"),
            ("━", self.colors['text_muted'], "Wall Barriers"),
        ]
        
        for i, (symbol, color, desc) in enumerate(legend_items):
            item_row = tk.Frame(legend_grid, bg=self.colors['card'])
            item_row.pack(fill='x', pady=2)
            
            symbol_label = tk.Label(
                item_row,
                text=symbol,
                font=('Segoe UI', 16, 'bold'),
                fg=color,
                bg=self.colors['card'],
                width=3
            )
            symbol_label.pack(side='left')
            
            desc_label = tk.Label(
                item_row,
                text=desc,
                font=('Segoe UI', 10, 'normal'),
                fg=self.colors['text_secondary'],
                bg=self.colors['card']
            )
            desc_label.pack(side='left', padx=(15, 0), anchor='w')
        
        # Setup enhanced button effects
        self.setup_button_effects()
    
    def setup_button_effects(self):
        def on_enter_primary(e):
            self.new_game_btn.config(bg=self.colors['primary_hover'], relief='raised')
        
        def on_leave_primary(e):
            self.new_game_btn.config(bg=self.colors['primary'], relief='raised')
        
        def on_enter_secondary(e):
            self.reset_btn.config(bg='#d97706', relief='raised')
        
        def on_leave_secondary(e):
            self.reset_btn.config(bg=self.colors['warning'], relief='raised')
        
        def on_enter_solution(e):
            self.show_solution_btn.config(bg='#7c3aed', relief='raised')
        
        def on_leave_solution(e):
            self.show_solution_btn.config(bg=self.colors['accent'], relief='raised')
        
        self.new_game_btn.bind("<Enter>", on_enter_primary)
        self.new_game_btn.bind("<Leave>", on_leave_primary)
        self.reset_btn.bind("<Enter>", on_enter_secondary)
        self.reset_btn.bind("<Leave>", on_leave_secondary)
        self.show_solution_btn.bind("<Enter>", on_enter_solution)
        self.show_solution_btn.bind("<Leave>", on_leave_solution)
    
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
        start_x = start_pos.col * self.cell_size + 20 + self.cell_size // 2
        start_y = start_pos.row * self.cell_size + 20 + self.cell_size // 2
        end_x = end_pos.col * self.cell_size + 20 + self.cell_size // 2
        end_y = end_pos.row * self.cell_size + 20 + self.cell_size // 2
        
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
        
        # Draw trajectory path as robot moves
        def animate_step(step):
            if step <= steps:
                current_x = start_x + step_x * step
                current_y = start_y + step_y * step
                
                # Draw path line from start to current position
                self.canvas.delete("trajectory_path")
                if step > 0:  # Only draw if robot has moved
                    self.canvas.create_line(
                        start_x, start_y, current_x, current_y,
                        fill='#38bdf8',  # Light blue path
                        width=3,
                        smooth=True,
                        tags="trajectory_path"
                    )
                
                # Update robot position (always on top)
                self.canvas.coords(
                    robot_id,
                    current_x - 25, current_y - 25,
                    current_x + 25, current_y + 25
                )
                
                self.root.after(20, lambda: animate_step(step + 1))
            else:
                # Clean up
                self.canvas.delete("trajectory_path")
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
        center_x = pos.col * self.cell_size + 20 + self.cell_size // 2
        center_y = pos.row * self.cell_size + 20 + self.cell_size // 2
        
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
        difficulty = self.difficulty_var.get()
        PuzzleGenerator.generate_guaranteed_solvable_puzzle(self.game, difficulty)
        self.last_optimal_moves = self.game.optimal_moves
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
    
    def show_solution(self):
        if self.game.game_won or self.show_win_overlay:
            return
        
        # Find the optimal solution using BFS
        solution_path = self.find_solution_path()
        
        if solution_path:
            self.animate_solution(solution_path)
        else:
            # Show message if no solution found
            self.show_no_solution_message()
    
    def find_solution_path(self):
        """Find the optimal solution path using BFS"""
        from collections import deque
        from puzzle_generator import PuzzleGenerator
        
        start = self.game.start_pos
        goal = self.game.goal_pos
        friend1 = self.game.friend1_pos
        friend2 = self.game.friend2_pos
        
        # State: (position, collected_items_set, path)
        queue = deque([(start, frozenset(), [])])
        visited = set()
        
        while queue:
            pos, collected, path = queue.popleft()
            
            state = (pos, collected)
            if state in visited:
                continue
            visited.add(state)
            
            # Win condition: goal is collected
            if goal in collected:
                return path
            
            # Try all directions
            for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
                new_pos, slide_path = self.game.ricochet_move(pos, direction)
                if new_pos == pos:
                    continue
                
                new_collected = set(collected)
                
                # Check what we collect during this slide
                for cell in slide_path[1:]:
                    if cell == friend1:
                        new_collected.add(friend1)
                    elif cell == friend2:
                        new_collected.add(friend2)
                    elif cell == goal and len(new_collected) == 2:
                        new_collected.add(goal)
                
                new_path = path + [direction]
                queue.append((new_pos, frozenset(new_collected), new_path))
        
        return None
    
    def animate_solution(self, solution_path):
        """Animate the solution step by step"""
        if not solution_path:
            return
        
        # Reset to start position
        self.reset_position()
        
        # Disable user input during animation
        self.is_animating = True
        
        def animate_next_move(move_index):
            if move_index >= len(solution_path):
                self.is_animating = False
                self.show_solution_complete_message()
                return
            
            direction = solution_path[move_index]
            result = self.game.move_robot(direction)
            
            if result:
                moved, old_pos, new_pos, friend_visited = result
                if moved:
                    # Animate this move
                    self.animate_robot_movement(old_pos, new_pos, friend_visited)
                    # Schedule next move after animation completes
                    self.root.after(1000, lambda: animate_next_move(move_index + 1))
                else:
                    animate_next_move(move_index + 1)
            else:
                animate_next_move(move_index + 1)
        
        # Start animation
        animate_next_move(0)
    
    def show_no_solution_message(self):
        """Show message when no solution is found"""
        # Create a temporary message overlay
        message_frame = tk.Frame(self.canvas, bg=self.colors['danger'])
        message_label = tk.Label(
            message_frame,
            text="No solution found!",
            font=('Segoe UI', 12, 'bold'),
            fg='white',
            bg=self.colors['danger']
        )
        message_label.pack(padx=10, pady=5)
        
        # Position in center of canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.canvas.create_window(
            canvas_width // 2, canvas_height // 2,
            window=message_frame
        )
        
        # Remove after 2 seconds
        self.root.after(2000, lambda: message_frame.destroy())
    
    def show_solution_complete_message(self):
        """Show message when solution animation completes"""
        # Create a temporary message overlay
        message_frame = tk.Frame(self.canvas, bg=self.colors['success'])
        message_label = tk.Label(
            message_frame,
            text="Solution demonstrated!",
            font=('Segoe UI', 12, 'bold'),
            fg='white',
            bg=self.colors['success']
        )
        message_label.pack(padx=10, pady=5)
        
        # Position in center of canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.canvas.create_window(
            canvas_width // 2, 50,
            window=message_frame
        )
        
        # Remove after 3 seconds
        self.root.after(3000, lambda: message_frame.destroy())
    
    def update_status(self):
        # Update optimal moves
        if self.game.optimal_moves is not None:
            self.optimal_moves_value.config(text=str(self.game.optimal_moves))
        else:
            self.optimal_moves_value.config(text="-")
        
        # Update moves
        self.moves_count_label.config(text=str(self.game.move_count))
        
        # Update crystal indicators
        
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
        # Draw enhanced grid with modern styling
        for i in range(5):
            for j in range(5):
                x1 = j * self.cell_size + 20
                y1 = i * self.cell_size + 20
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Modern cell colors with subtle gradients
                if (i + j) % 2 == 0:
                    fill_color = '#ffffff'
                    border_color = '#e2e8f0'
                else:
                    fill_color = '#f8fafc'
                    border_color = '#cbd5e1'
                
                # Enhanced highlight for visited friends
                if Position(i, j) in self.game.visited_friends:
                    fill_color = '#d1fae5'
                    border_color = '#10b981'
                
                # Create cell with subtle shadow effect
                self.canvas.create_rectangle(
                    x1 + 1, y1 + 1, x2 + 1, y2 + 1,
                    fill='#e5e7eb', outline='', width=0
                )
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill_color, outline=border_color, width=2
                )
                
                # Draw cell content
                cell_type = self.game.grid[i][j]
                center_x = x1 + self.cell_size // 2
                center_y = y1 + self.cell_size // 2
                
                if cell_type == CellType.ROBOT:
                    # Enhanced robot with modern design
                    # Outer glow
                    self.canvas.create_oval(
                        x1 + 8, y1 + 8, x2 - 8, y2 - 8,
                        fill='#a7f3d0', outline='', width=0
                    )
                    # Main robot body
                    self.canvas.create_oval(
                        x1 + 12, y1 + 12, x2 - 12, y2 - 12,
                        fill=self.colors['secondary'], outline='#0891b2', width=3
                    )
                    # Inner highlight
                    self.canvas.create_oval(
                        center_x - 10, center_y - 10, center_x + 10, center_y + 10,
                        fill='#bfdbfe', outline=''
                    )
                    # Core dot
                    self.canvas.create_oval(
                        center_x - 4, center_y - 4, center_x + 4, center_y + 4,
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
                    # Enhanced goal with pulsing effect
                    # Outer glow
                    glow_points = [
                        center_x, y1 + 10,
                        x2 - 10, center_y,
                        center_x, y2 - 10,
                        x1 + 10, center_y
                    ]
                    self.canvas.create_polygon(
                        glow_points, fill='#fecaca', outline=''
                    )
                    # Main diamond
                    points = [
                        center_x, y1 + 18,
                        x2 - 18, center_y,
                        center_x, y2 - 18,
                        x1 + 18, center_y
                    ]
                    self.canvas.create_polygon(
                        points, fill=self.colors['danger'], outline='#991b1b', width=3
                    )
                    # Inner shine
                    inner_points = [
                        center_x, y1 + 28,
                        x2 - 28, center_y,
                        center_x, y2 - 28,
                        x1 + 28, center_y
                    ]
                    self.canvas.create_polygon(
                        inner_points, fill='#fca5a5', outline=''
                    )
                    # Central sparkle
                    self.canvas.create_oval(
                        center_x - 3, center_y - 3, center_x + 3, center_y + 3,
                        fill='white', outline=''
                    )
                
                elif cell_type == CellType.FRIEND1:
                    # Enhanced amber crystal
                    # Glow effect
                    glow_points = [
                        center_x, y1 + 10,
                        x2 - 10, y2 - 10,
                        x1 + 10, y2 - 10
                    ]
                    self.canvas.create_polygon(
                        glow_points, fill='#fed7aa', outline=''
                    )
                    # Main crystal
                    points = [
                        center_x, y1 + 18,
                        x2 - 18, y2 - 18,
                        x1 + 18, y2 - 18
                    ]
                    self.canvas.create_polygon(
                        points, fill=self.colors['warning'], outline='#d97706', width=3
                    )
                    # Inner shine
                    shine_points = [
                        center_x, y1 + 28,
                        x2 - 28, y2 - 28,
                        x1 + 28, y2 - 28
                    ]
                    self.canvas.create_polygon(
                        shine_points, fill='#fcd34d', outline=''
                    )
                    # Highlight
                    self.canvas.create_polygon([
                        center_x, y1 + 23,
                        center_x + 8, center_y + 2,
                        center_x - 8, center_y + 2
                    ], fill='#fef3c7', outline='')
                
                elif cell_type == CellType.FRIEND2:
                    # Enhanced violet crystal
                    # Glow effect
                    glow_points = [
                        x1 + 10, y1 + 10,
                        x2 - 10, y1 + 10,
                        center_x, y2 - 10
                    ]
                    self.canvas.create_polygon(
                        glow_points, fill='#ddd6fe', outline=''
                    )
                    # Main crystal
                    points = [
                        x1 + 18, y1 + 18,
                        x2 - 18, y1 + 18,
                        center_x, y2 - 18
                    ]
                    self.canvas.create_polygon(
                        points, fill=self.colors['accent'], outline='#7c3aed', width=3
                    )
                    # Inner shine
                    shine_points = [
                        x1 + 28, y1 + 28,
                        x2 - 28, y1 + 28,
                        center_x, y2 - 28
                    ]
                    self.canvas.create_polygon(
                        shine_points, fill='#c4b5fd', outline=''
                    )
                    # Highlight
                    self.canvas.create_polygon([
                        center_x - 8, y1 + 23,
                        center_x + 8, y1 + 23,
                        center_x, center_y + 2
                    ], fill='#e0e7ff', outline='')
        
        # Draw walls with 3D effect
        self.draw_walls()
    
    def draw_walls(self):
        for wall in self.game.walls:
            a, b = wall.from_pos, wall.to_pos
            valid_a = self.game.is_valid_position(a)
            valid_b = self.game.is_valid_position(b)
            if valid_a and valid_b:
                from_x = a.col * self.cell_size + 20
                from_y = a.row * self.cell_size + 20
                to_x = b.col * self.cell_size + 20
                to_y = b.row * self.cell_size + 20
                # Enhanced vertical wall
                if a.row == b.row:
                    wall_x = max(from_x, to_x)
                    wall_y1 = from_y + 10
                    wall_y2 = from_y + self.cell_size - 10
                    
                    # Shadow
                    self.canvas.create_line(
                        wall_x + 1, wall_y1 + 1, wall_x + 1, wall_y2 + 1,
                        fill='#9ca3af', width=self.wall_thickness, capstyle='round'
                    )
                    # Main wall
                    self.canvas.create_line(
                        wall_x, wall_y1, wall_x, wall_y2,
                        fill='#374151', width=self.wall_thickness, capstyle='round'
                    )
                    # Highlight
                    self.canvas.create_line(
                        wall_x - 1, wall_y1, wall_x - 1, wall_y2,
                        fill='#94a3b8', width=2, capstyle='round'
                    )
                
                # Enhanced horizontal wall
                elif a.col == b.col:
                    wall_y = max(from_y, to_y)
                    wall_x1 = from_x + 10
                    wall_x2 = from_x + self.cell_size - 10
                    
                    # Shadow
                    self.canvas.create_line(
                        wall_x1 + 1, wall_y + 1, wall_x2 + 1, wall_y + 1,
                        fill='#9ca3af', width=self.wall_thickness, capstyle='round'
                    )
                    # Main wall
                    self.canvas.create_line(
                        wall_x1, wall_y, wall_x2, wall_y,
                        fill='#374151', width=self.wall_thickness, capstyle='round'
                    )
                    # Highlight
                    self.canvas.create_line(
                        wall_x1, wall_y - 1, wall_x2, wall_y - 1,
                        fill='#94a3b8', width=2, capstyle='round'
                    )
            elif valid_a and not valid_b:
                x = a.col * self.cell_size + 20
                y = a.row * self.cell_size + 20
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