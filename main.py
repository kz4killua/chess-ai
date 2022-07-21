import tkinter as tk
import tkinter.messagebox

import chess
from PIL import ImageTk, Image
from minimax import Agent

CELL_WIDTH = 70
ICON_WIDTH = int(CELL_WIDTH * 0.8)

# Initialize the root widget.
root = tk.Tk()
root.geometry(f'{CELL_WIDTH * 8}x{CELL_WIDTH * 8}')
root.title('Chess')

MOVE_ANIMATION_SPEED = CELL_WIDTH / 50
ILLEGAL_MOVE_REVERSE_ANIMATION_SPEED = CELL_WIDTH / 25

def load_icons(path):
    """Loads all the icons in a folder and returns a dictionary mapping each icon to its name."""
    return {
        chess.WHITE:{
            chess.KING:   ImageTk.PhotoImage(Image.open(path + '/WK.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.QUEEN:  ImageTk.PhotoImage(Image.open(path + '/WQ.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.ROOK:   ImageTk.PhotoImage(Image.open(path + '/WR.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.KNIGHT: ImageTk.PhotoImage(Image.open(path + '/WN.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.BISHOP: ImageTk.PhotoImage(Image.open(path + '/WB.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.PAWN:   ImageTk.PhotoImage(Image.open(path + '/WP.png').resize((ICON_WIDTH, ICON_WIDTH)))
        },  
        chess.BLACK:{
            chess.KING:   ImageTk.PhotoImage(Image.open(path + '/BK.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.QUEEN: ImageTk.PhotoImage(Image.open(path + '/BQ.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.ROOK:  ImageTk.PhotoImage(Image.open(path + '/BR.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.KNIGHT:ImageTk.PhotoImage(Image.open(path + '/BN.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.BISHOP:ImageTk.PhotoImage(Image.open(path + '/BB.png').resize((ICON_WIDTH, ICON_WIDTH))),
            chess.PAWN:  ImageTk.PhotoImage(Image.open(path + '/BP.png').resize((ICON_WIDTH, ICON_WIDTH)))
        }
    }

class LocalGame:

    def __init__(self, white, black):
        self.board = chess.Board()
        self.white = white
        self.black = black

class Player:
    
    def __init__(self, name):
        self.name = name        
        
class GUI:

    def __init__(self, root):
        
        # Set up the root widget.
        self.root = root

        # Create a game.
        p1 = Player('1')
        p2 = Agent()
        self.game = LocalGame(p1, p2)

        # Set up the board widget.
        self.board_widget = BoardWidget(root, self.game.board, THEMES['Purple'], chess.WHITE)
        
        # Draw the widget on the screen.
        self.board_widget.canvas.grid(row=0, column=0)

    def ai_move(self):
        """Makes an AI move"""
        if self.game.board.turn == chess.BLACK:
            # Use minimax to get the best move
            move = self.game.black.minimax(self.game.board, 2, float('-inf'), float('+inf'), self.game.board.turn)[0]
            # Make the move
            self.board_widget.make_move(move)
        self.root.after(1000, self.ai_move)


    def mainloop(self):
        """Starts and runs the GUI."""
        self.root.after(1000, self.ai_move)
        self.root.mainloop()


class BoardWidget:

    # TODO: Flipping the board.

    def __init__(self, root, board, theme, pov):
        self.root = root
        self.board = board
        self.theme = theme
        self.canvas = tk.Canvas(self.root, width=CELL_WIDTH * 8, height=CELL_WIDTH * 8) 
        self.pov = pov
        self.active_square = None
        self.icon_tags = {}
        self.square_tags = {}
        self.highlights = []

        # Add functions.
        self.canvas.bind('<B1-Motion>', self.mouse_drag)
        self.canvas.bind('<ButtonPress-1>', self.mouse_click)
        self.canvas.bind('<ButtonRelease-1>', self.mouse_release)

        # Draw the board.
        self.draw_board()

    def _draw_squares(self):
        """Draws squares on the board."""

        self.square_tags.clear()

        for square in chess.SQUARES:

            if self.pov == chess.BLACK:
                square = 63 - square

            if 1 << square & chess.BB_DARK_SQUARES:
                fill = self.theme['dark_square_colour']
            else:
                fill = self.theme['light_square_colour']

            row, col = square // 8, square % 8

            x0 = row * CELL_WIDTH
            y0 = col * CELL_WIDTH
            x1 = (row + 1) * CELL_WIDTH
            y1 = (col + 1) * CELL_WIDTH

            self.square_tags[square] = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, 
                outline=self.theme['outline_colour'], width=self.theme['outline_width'])

    def _draw_labels(self):
        """Draws rank and file labels."""

        font_size = CELL_WIDTH // 5
        font_face = 'Helvetica'
        font = (font_face, font_size)

        file_labels = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        rank_labels = ('1', '2', '3', '4', '5', '6', '7', '8')

        if self.pov == chess.BLACK:
            file_labels = reversed(file_labels)
            rank_labels = reversed(rank_labels)

        # Draw file labels.
        for file_number, file_label  in enumerate(file_labels):

            if file_number % 2 == 0:
                fill = self.theme['dark_square_colour']
            else:
                fill = self.theme['light_square_colour'] 

            x = (file_number + 1) * CELL_WIDTH - font_size + font_size // 5
            y = CELL_WIDTH * 8 - font_size - font_size // 5

            self.canvas.create_text(x, y, fill=fill, font=font, text=file_label)

        # Draw rank labels.
        for rank_number, rank_label in enumerate(rank_labels):

            if rank_number % 2 == 0:
                fill = self.theme['dark_square_colour']
            else:
                fill = self.theme['light_square_colour']

            x = 0 * CELL_WIDTH + (2 * font_size // 5)
            y = (CELL_WIDTH * (7 - rank_number)) + (2 * font_size // 5)

            self.canvas.create_text(x, y, fill=fill, font=font, text=rank_label) 

    def _draw_pieces(self):
        """Draws the pieces on the board."""

        self.icon_tags.clear()

        # Draw each piece.
        for colour in chess.COLORS:
            for piece_type in chess.PIECE_TYPES:

                icon = self.theme['icons'][colour][piece_type]

                for square in self.board.pieces(piece_type, colour):

                    row, col = square // 8, square % 8

                    if self.pov == chess.BLACK:
                        row = 7 - row
                        col = 7 - col

                    left = col * CELL_WIDTH + (CELL_WIDTH // 2)
                    top = (7 - row) * CELL_WIDTH + (CELL_WIDTH // 2)

                    self.icon_tags[square] = self.canvas.create_image(left, top, image=icon)

    def draw_board(self):
        """Draws the board."""

        self._draw_squares()
        self._draw_labels()
        self._draw_pieces()

    def highlight_previous_move(self, move):
        """Highlights the last move made on the board."""

        for square in (move.from_square, move.to_square):

            row, col = square // 8, square % 8

            if self.pov == chess.BLACK:
                row = 7 - row
                col = 7 - col
                
            x0 = col * CELL_WIDTH
            y0 = (7 - row) * CELL_WIDTH
            x1 = (col + 1) * CELL_WIDTH
            y1 = (7 - row + 1) * CELL_WIDTH

            self.highlights.append(self.canvas.create_rectangle(x0, y0, x1, y1, 
                fill=self.theme['square_highlight_colour'], 
                outline=self.theme['outline_colour'], 
                width=self.theme['outline_width']))

    def _highlight_capture_square(self, square):
        """Highlights a square that a piece can capture on."""
        
        row, col = square // 8, square % 8
                
        if self.pov == chess.BLACK:
            row = 7 - row
            col = 7 - col

        x0 = col * CELL_WIDTH
        y0 = (7 - row) * CELL_WIDTH
        x1 = x0 + CELL_WIDTH // 5
        y1 = y0
        x2 = x0
        y2 = y0 + CELL_WIDTH // 5
        self.highlights.append(self.canvas.create_polygon([x0, y0, x1, y1, x2, y2], fill=self.theme['capture_square_highlight_colour']))

        x0 = (col + 1) * CELL_WIDTH
        y0 = (7 - row) * CELL_WIDTH
        x1 = x0 - CELL_WIDTH // 5
        y1 = y0
        x2 = x0
        y2 = y0 + CELL_WIDTH // 5
        self.highlights.append(self.canvas.create_polygon([x0, y0, x1, y1, x2, y2], fill=self.theme['capture_square_highlight_colour']))

        x0 = col * CELL_WIDTH
        y0 = (7 - row + 1) * CELL_WIDTH
        x1 = x0 + CELL_WIDTH // 5
        y1 = y0
        x2 = x0
        y2 = y0 - CELL_WIDTH // 5
        self.highlights.append(self.canvas.create_polygon([x0, y0, x1, y1, x2, y2], fill=self.theme['capture_square_highlight_colour']))

        x0 = (col + 1) * CELL_WIDTH
        y0 = (7 - row + 1) * CELL_WIDTH
        x1 = x0 - CELL_WIDTH // 5
        y1 = y0
        x2 = x0
        y2 = y0 - CELL_WIDTH // 5
        self.highlights.append(self.canvas.create_polygon([x0, y0, x1, y1, x2, y2], fill=self.theme['capture_square_highlight_colour']))

    def _highlight_non_capture_square(self, square):
        """Highlights a square that a piece can move to."""

        row, col = square // 8, square % 8

        if self.pov == chess.BLACK:
            row = 7 - row
            col = 7 - col
                    
        x0 = col * CELL_WIDTH + (CELL_WIDTH - CELL_WIDTH // 5) // 2
        y0 = (7 - row) * CELL_WIDTH + (CELL_WIDTH - CELL_WIDTH // 5) // 2
        x1 = x0 + CELL_WIDTH // 5
        y1 = y0 + CELL_WIDTH // 5

        self.highlights.append(self.canvas.create_oval(x0, y0, x1, y1, 
            fill=self.theme['non_capture_square_highlight_colour'], width=0))

    def highlight_possible_moves(self):
        """Highlights legal moves that can be made on the board."""

        for move in self.board.legal_moves:

            if move.from_square == self.active_square:

                if self.board.is_capture(move):
                    self._highlight_capture_square(move.to_square)
                else:
                    self._highlight_non_capture_square(move.to_square)

    def clear_highlights(self):
        """Removes all highlights on the board."""
        self.canvas.delete(*self.highlights)
        self.highlights.clear()

    def clear_pieces(self):
        """Removes all pieces on the board."""
        self.canvas.delete(*self.icon_tags)
        self.icon_tags.clear()

    def set_active(self, square):
        """Sets a square as active."""
        self.clear_highlights()
        # Update the active square.
        self.active_square = square
        # Highlight possible moves.
        self.highlight_possible_moves()
        # Find the icon on that square.
        tag = self.icon_tags[square]
        # Move the icon to the topmost level.
        self.canvas.tag_raise(tag)

    def make_move(self, move):
        """Makes a move on the board."""
        self.highlight_previous_move(move)
        self.animate_move(move)
        self.board.push(move)
        self.active_square = None

        # Check for game end.
        if self.board.is_game_over(claim_draw=True):
            result = self.board.result()
            self.display_result(result)

    def mouse_click(self, event):
        """Handler for mouse click events."""

        # Check which square was just clicked on.
        r = 7 - event.y // CELL_WIDTH
        c = event.x // CELL_WIDTH
        square = r * 8 + c
        
        if self.pov == chess.BLACK:
            square = 63 - square

        # If there is a legal move from that square, set it as active.
        for move in self.board.legal_moves:
            if move.from_square == square:
                self.set_active(square)
                break

    def mouse_drag(self, event):
        """Handler for mouse drag events."""

        if self.active_square is not None and (self.board.occupied & (1 << self.active_square)):
            # Find the icon for that square.
            tag = self.icon_tags[self.active_square]
            # Move the piece.
            x = event.x - ICON_WIDTH // 2
            y = event.y - ICON_WIDTH // 2
            self.canvas.moveto(tag, x=x, y=y)

    def mouse_release(self, event):
        """Handler for mouse release events."""

        # Check which square was just clicked on.
        r = 7 - event.y // CELL_WIDTH
        c = event.x // CELL_WIDTH
        square = r * 8 + c

        if self.pov == chess.BLACK:
            square = 63 - square

        if not self.board.occupied & (1 << square):
            self.clear_highlights()

        if self.active_square is not None:
            
            for move in self.board.legal_moves:

                # If there is a legal move to that square, make the move.
                if move.from_square == self.active_square and move.to_square == square:

                    if move.promotion:
                        promotion = self.get_promotion()
                    else:
                        promotion = ''
                    
                    # Construct a move object.
                    uci = chess.SQUARE_NAMES[self.active_square] + chess.SQUARE_NAMES[square] + promotion
                    move = chess.Move.from_uci(uci)

                    self.clear_highlights()

                    # Carry out the move.
                    self.make_move(move)
                    break
            
            # If no legal moves, animate the icon back to its square.
            else:
                tag = self.icon_tags[self.active_square]
                self.animate_motion(tag, self.active_square, ILLEGAL_MOVE_REVERSE_ANIMATION_SPEED)

    def animate_motion(self, tag, dest, speed):
        """Animate the movement of an object identified by its tag to a destination square."""
            
        # Calculate the source coordinates.
        src_coords = self.canvas.coords(tag)
        src_coords[0] -= ICON_WIDTH // 2
        src_coords[1] -= ICON_WIDTH // 2

        # Calculate the destination coordinates.
        row, col = dest // 8, dest % 8

        if self.pov == chess.BLACK:
            row = 7 - row
            col = 7 - col

        left = col * CELL_WIDTH + (CELL_WIDTH // 2) - ICON_WIDTH // 2
        top = (7 - row) * CELL_WIDTH + (CELL_WIDTH // 2) - ICON_WIDTH // 2
        dest_coords = left, top

        # Calculate the horizontal and vertical distances.
        delta_x = dest_coords[0] - src_coords[0]
        delta_y = dest_coords[1] - src_coords[1]
        # Calculate the straight line distance.
        distance = (delta_x ** 2 + delta_y ** 2) ** 0.5
        # Check how many steps it will take to get to the destination.
        steps = int(distance / speed)
        
        # Move the piece.
        position = src_coords[:]
        for i in range(steps):
            x = position[0] + delta_x / steps
            y = position[1] + delta_y / steps
            self.canvas.moveto(tag, x, y)
            position = [x, y]
            self.root.update_idletasks()

        # Ensure the icon is at the correct position.
        self.canvas.moveto(tag, *dest_coords)
        self.root.update_idletasks()

    def _animate_castling_move(self, move):
        """Animates a castling move."""

        king_src = move.from_square
        king_dest = move.to_square

        # Check the position and destination of the moving rook.
        if self.board.is_kingside_castling(move):

            if self.board.turn == chess.WHITE:
                rook_src = chess.H1
                rook_dest = chess.F1
            else:
                rook_src = chess.H8
                rook_dest = chess.F8
            
        else:

            if self.board.turn == chess.WHITE:
                rook_src = chess.A1
                rook_dest = chess.D1
            else:
                rook_src = chess.A8
                rook_dest = chess.D8

        king_tag = self.icon_tags[king_src]
        rook_tag = self.icon_tags[rook_src]

        self.canvas.tag_raise(king_tag)
        self.canvas.tag_raise(rook_tag)

        self.animate_motion(king_tag, king_dest, speed=MOVE_ANIMATION_SPEED)
        self.animate_motion(rook_tag, rook_dest, speed=MOVE_ANIMATION_SPEED)

        # Update icon mappings.
        del self.icon_tags[king_src]
        self.icon_tags[king_dest] = king_tag
        del self.icon_tags[rook_src]
        self.icon_tags[rook_dest] = rook_tag

    def _animate_promotion_move(self, move):
        """Animates a promotion move."""

        src = move.from_square
        dest = move.to_square
        icon_tag = self.icon_tags[src]

        self.canvas.tag_raise(icon_tag)

        # Move the piece.
        self.animate_motion(icon_tag, dest, speed=MOVE_ANIMATION_SPEED)

        # Replace pawn with promoted piece.
        promotion_icon = self.theme['icons'][self.board.turn][move.promotion]
        left, top = self.canvas.coords(icon_tag)
        self.canvas.delete(icon_tag)            
        promotion_icon_tag = self.canvas.create_image(left, top, image=promotion_icon)

        # Make captures if necessary.
        if self.board.is_capture(move):
            capture_square = dest
            capture_tag = self.icon_tags[capture_square]
            self.canvas.delete(capture_tag)
            del self.icon_tags[capture_square]

        # Update icon mappings.
        del self.icon_tags[src]
        self.icon_tags[dest] = promotion_icon_tag

    def _animate_regular_move(self, move):
        """Animate a non-castling, non_promotion move."""
        src = move.from_square
        dest = move.to_square
        icon_tag = self.icon_tags[src]

        self.canvas.tag_raise(icon_tag)

        # Move the piece.
        self.animate_motion(icon_tag, dest, speed=MOVE_ANIMATION_SPEED)

        # Check for captures.
        if self.board.is_capture(move):

            if self.board.is_en_passant(move):

                if self.board.turn == chess.WHITE:
                    capture_square = move.to_square - 8
                else:
                    capture_square = move.to_square + 8

            else:
                capture_square = dest

            # Get the icon tag of the piece to be captured.
            capture_tag = self.icon_tags[capture_square]
            self.canvas.delete(capture_tag)
            del self.icon_tags[capture_square]
            
        # Update icon mappings.
        del self.icon_tags[src]
        self.icon_tags[dest] = icon_tag

    def animate_move(self, move):
        """Animates a move on the board."""

        # Animate castling moves.
        if self.board.is_castling(move):
            self._animate_castling_move(move)

        # Animate promotions.
        elif move.promotion:
            self._animate_promotion_move(move)

        else:
            self._animate_regular_move(move)
            
    def get_promotion(self):
        
        promotion = tk.StringVar()

        # Create a new top-level window.
        promotion_window = tk.Toplevel(self.root, height=CELL_WIDTH * 4, width=CELL_WIDTH * 4)
        promotion_window.geometry(f'{CELL_WIDTH * 4}x{CELL_WIDTH * 4}')
        promotion_window.title('Select promotion type.')

        # Create a frame.
        frame = tk.Frame(promotion_window, width=CELL_WIDTH * 4, height=CELL_WIDTH * 4)

        # Get all icons.
        frame.rook_icon = self.theme['icons'][self.board.turn][chess.ROOK]
        frame.knight_icon = self.theme['icons'][self.board.turn][chess.KNIGHT]
        frame.bishop_icon = self.theme['icons'][self.board.turn][chess.BISHOP]
        frame.queen_icon = self.theme['icons'][self.board.turn][chess.QUEEN]

        # Make four buttons for each promotion type.
        rook = tk.Button(frame, width=CELL_WIDTH * 2, height=CELL_WIDTH * 2, image=frame.rook_icon, command=lambda: promotion.set('r'))
        knight = tk.Button(frame, width=CELL_WIDTH * 2, height=CELL_WIDTH * 2, image=frame.knight_icon, command=lambda: promotion.set('n'))
        bishop = tk.Button(frame, width=CELL_WIDTH * 2, height=CELL_WIDTH * 2, image=frame.bishop_icon, command=lambda: promotion.set('b'))
        queen = tk.Button(frame, width=CELL_WIDTH * 2, height=CELL_WIDTH * 2, image=frame.queen_icon, command=lambda: promotion.set('q'))

        # Put the buttons on the frame.
        rook.grid(row=0, column=0)
        knight.grid(row=0, column=1)
        bishop.grid(row=1, column=0)
        queen.grid(row=1, column=1)

        frame.pack()

        promotion_window.attributes('-topmost', 1)
        promotion_window.wait_variable(promotion)
        promotion_window.destroy()

        return promotion.get()

    def display_result(self, result):
        
        if result == '1-0':
            tkinter.messagebox.showinfo('Game Over', 'Checkmate! White wins.')
        elif result == '0-1':
            tkinter.messagebox.showinfo('Game Over', 'Checkmate! Black wins.')
        elif result == '1/2-1/2':
            tkinter.messagebox.showinfo('Game Over', 'Draw')


DEFAULT_ICONS = load_icons('resources/images/icons/001')

THEMES = {
    'Green': {
        'light_square_colour': '#f0fff0',
        'dark_square_colour': '#4bc84b',
        'outline_colour': '#000000',
        'outline_width': 0,
        'square_highlight_colour': '#649696',
        'non_capture_square_highlight_colour': '#649696',
        'capture_square_highlight_colour': '#323232',
        'icons': DEFAULT_ICONS
    },
    'Blue': {
        'light_square_colour': '#f0f0ff',
        'dark_square_colour': '#4b4bc8',
        'outline_colour': '#000000',
        'outline_width': 0,
        'square_highlight_colour': '#649696',
        'non_capture_square_highlight_colour': '#649696',
        'capture_square_highlight_colour': '#323232',
        'icons': DEFAULT_ICONS
    },
    'Purple': {
        'light_square_colour': '#fff0ff',
        'dark_square_colour': '#aa00dc',
        'outline_colour': '#000000',
        'outline_width': 0,
        'square_highlight_colour': '#649696',
        'non_capture_square_highlight_colour': '#82b4b4',
        'capture_square_highlight_colour': '#649696',
        'icons': DEFAULT_ICONS
    },
    'High Contrast': {
        'light_square_colour': '#ffffff',
        'dark_square_colour': '#000000',
        'outline_colour': '#cd7400',
        'outline_width': 3,
        'square_highlight_colour': '#cd7400',
        'non_capture_square_highlight_colour': '#cd7400',
        'capture_square_highlight_colour': '#cd7400',
        'icons': DEFAULT_ICONS
    }
}


def main():
    """Starts the application."""
    gui = GUI(root)
    gui.mainloop()

if __name__ == '__main__':
    main()
