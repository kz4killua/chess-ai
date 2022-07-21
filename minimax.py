import random

import chess

class Agent:

    def __init__(self, custom_evaluation=None):
        if custom_evaluation:
            self.calculate_static_evaluation = custom_evaluation

    def minimax(self, board, depth, alpha, beta, is_maximizer):

        # At terminal nodes, return a static evaluation.
        if depth == 0 or board.is_game_over(claim_draw=True):
            return None, self.calculate_static_evaluation(board)

        # Start by picking a random best move.
        best_move = random.choice(list(board.legal_moves))

        if is_maximizer:
            max_eval = float('-inf')
            for move in board.legal_moves:

                # Make the move.
                board.push(move)
                # Evaluate the board.
                evaluation = self.minimax(board, depth-1, alpha, beta, False)[1]
                # Unmake the move.
                board.pop()

                # Update the best move.
                if evaluation > max_eval:
                    best_move = move
                # Update the best evaluation.
                max_eval = max(evaluation, max_eval)
                # Update alpha.
                alpha = max(alpha, evaluation)

                # Check for cut-offs.
                if beta <= alpha:
                    break

            return (best_move, max_eval)
        
        else:
            min_eval = float('+inf')
            for move in board.legal_moves:

                # Make the move.
                board.push(move)
                # Evaluate the board.
                evaluation = self.minimax(board, depth-1, alpha, beta, True)[1]
                # Unmake the move.
                board.pop()

                # Update the best move.
                if evaluation < min_eval:
                    best_move = move
                # Update the best evaluation.
                min_eval = min(evaluation, min_eval)
                # Update beta.
                beta = min(beta, evaluation)

                # Check for cut-offs.
                if beta <= alpha:
                    break

            return (best_move, min_eval)

    def calculate_static_evaluation(self, board):
        """Returns a static evaluation of a board state."""

        # Evaluate terminal states.
        if board.is_game_over(claim_draw=True):
            result = board.result(claim_draw=True)
            if result == '1-0':
                return +1_000_000
            elif result == '0-1':
                return -1_000_000
            else:
                return 0

        centipawn_evaluation = 0

        # Evaluate material.
        material_balance = 0
        material_balance += len(board.pieces(chess.PAWN, chess.WHITE)) * +100
        material_balance += len(board.pieces(chess.PAWN, chess.BLACK)) * -100
        material_balance += len(board.pieces(chess.ROOK, chess.WHITE)) * +500
        material_balance += len(board.pieces(chess.ROOK, chess.BLACK)) * -500
        material_balance += len(board.pieces(chess.KNIGHT, chess.WHITE)) * +300
        material_balance += len(board.pieces(chess.KNIGHT, chess.BLACK)) * -300
        material_balance += len(board.pieces(chess.BISHOP, chess.WHITE)) * +300
        material_balance += len(board.pieces(chess.BISHOP, chess.BLACK)) * -300
        material_balance += len(board.pieces(chess.QUEEN, chess.WHITE)) * +900
        material_balance += len(board.pieces(chess.QUEEN, chess.BLACK)) * -900

        # TODO: Evaluate mobility.
        mobility = 0

        # Aggregate values.
        centipawn_evaluation = material_balance + mobility

        return centipawn_evaluation

def main():
    
    m1 = chess.Board('8/8/7k/8/8/8/5R2/6R1 w - - 0 1') # f2h2
    m2 = chess.Board('8/6k1/8/8/8/8/1K2R3/5R2 w - - 0 1') # e2g2
    m3 = chess.Board('8/8/5k2/8/8/8/3R4/4R3 w - - 0 1') # d2f2

    agent = Agent()

    # print(agent.minimax(m1, 2, float('-inf'), float('+inf'), True)[0])
    # print(agent.minimax(m2, 4, float('-inf'), float('+inf'), True)[0])
    # print(agent.minimax(m3, 6, float('-inf'), float('+inf'), True)[0])


if __name__ == '__main__':
    main()
